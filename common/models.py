import uuid

from crum import get_current_user
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


# from accounts.models import User
class TimeAuditModel(models.Model):
    """To path when the record was created and last modified"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")

    class Meta:
        abstract = True


class UserAuditModel(models.Model):
    """To path when the record was created and last modified"""

    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name="%(class)s_created_by",
        verbose_name="Created By",
        null=True,
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated_by",
        verbose_name="Last Modified By",
        null=True,
    )

    class Meta:
        abstract = True


class SoftDeletionQuerySet(models.QuerySet):
    def delete(self, soft=True):
        if soft:
            return self.update(deleted_at=timezone.now())
        else:
            return super().delete()


class SoftDeletionManager(models.Manager):
    def get_queryset(self):
        return SoftDeletionQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True
        )


class SoftDeleteModel(models.Model):
    """To soft delete records"""

    deleted_at = models.DateTimeField(verbose_name="Deleted At", null=True, blank=True)

    objects = SoftDeletionManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, soft=True, *args, **kwargs):
        user = get_current_user()
        content_type = ContentType.objects.get_for_model(self.__class__)

        if soft:
            # Soft delete the current instance
            self.deleted_at = timezone.now()
            self.save(using=using)

            # soft_delete_related_objects.delay(
            #     self._meta.app_label, self._meta.model_name, self.pk, using=using
            # )

            # 🔐 Log soft delete
            AuditLog.objects.create(
                user=user if user and not user.is_anonymous else None,
                action='delete',
                content_type=content_type,
                object_id=str(self.pk),
                changes={"type": "soft", "deleted_at": self.deleted_at.isoformat()},
            )

        else:
            # 🔐 Log hard delete BEFORE the actual delete
            AuditLog.objects.create(
                user=user if user and not user.is_anonymous else None,
                action='delete',
                content_type=content_type,
                object_id=str(self.pk),
                changes={"type": "hard"},
            )

            # Perform hard delete if soft deletion is not enabled
            return super().delete(using=using, *args, **kwargs)


class AuditModel(TimeAuditModel, UserAuditModel, SoftDeleteModel):
    """To path when the record was created and last modified"""

    class Meta:
        abstract = True


class BaseModel(AuditModel):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True, primary_key=True
    )

    class Meta:
        abstract = True

    def save(self, *args, created_by_id=None, disable_auto_set_user=False, **kwargs):
        if not disable_auto_set_user:
            # Check if created_by_id is provided
            if created_by_id:
                self.created_by_id = created_by_id
            else:
                user = get_current_user()

                if user is None or user.is_anonymous:
                    self.created_by = None
                    self.updated_by = None
                else:
                    # Check if the model is being created or updated
                    if self._state.adding:
                        # If creating, set created_by and leave updated_by as None
                        self.created_by = user
                        self.updated_by = None
                    else:
                        # If updating, set updated_by only
                        self.updated_by = user

        super(BaseModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class SimpleModel(models.Model):
    """
    This is a basic model used to illustrate a many-to-many relationship
    with RandomModel.
    """

    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, blank=True, null=True)


class RandomModel(BaseModel):
    """
    This is an example model, to be used as reference in the Styleguide,
    when discussing model validation via constraints.
    """

    start_date = models.DateField()
    end_date = models.DateField()

    simple_objects = models.ManyToManyField(
        SimpleModel, blank=True, related_name="random_objects"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="start_date_before_end_date", check=Q(start_date__lt=F("end_date"))
            )
        ]


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    user = models.ForeignKey(
        'users.User', null=True, blank=True, on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100)
    content_object = GenericForeignKey("content_type", "object_id")

    # Store the diff or full data snapshot
    changes = models.JSONField()

    def __str__(self):
        return f"{self.get_action_display()} - {self.content_type} - {self.object_id}"


class APIActivityLog(BaseModel):
    token_identifier = models.CharField(max_length=255)

    # Request Info
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    query_params = models.TextField(null=True, blank=True)
    headers = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)

    # Response info
    response_code = models.PositiveIntegerField()
    response_body = models.TextField(null=True, blank=True)

    # Meta information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        verbose_name = "API Activity Log"
        verbose_name_plural = "API Activity Logs"
        db_table = "api_activity_logs"
        ordering = ("-created_at",)

    def __str__(self):
        return str(self.token_identifier)


class ErrorLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    exception_type = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    stack_trace = models.TextField(blank=True, null=True)
    user = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.SET_NULL)
    headers = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
