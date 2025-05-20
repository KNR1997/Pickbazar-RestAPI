from typing import List, Optional

from django.db import transaction

from common.services import model_update
from users.models import User, Profile
from users.services.address_services import address_create


@transaction.atomic
def user_create(*, email: str,
                password: Optional[str] = None
                ) -> User:
    user = User.objects.create_user(email=email,
                                    password=password,
                                    )

    return user


@transaction.atomic
def user_update(*, user: User, data) -> User:
    non_side_effect_fields: List[str] = [
        "name",
    ]

    user, has_updated = model_update(instance=user, fields=non_side_effect_fields, data=data)

    # Handle profile update or creation
    profile_data = data.get("profile")
    if profile_data:
        profile, _ = Profile.objects.get_or_create(user=user)  # Get or create Profile instance
        for key, value in profile_data.items():
            setattr(profile, key, value)
        profile.save()

    # Handle address update
    address_list = data.get("address", [])
    if address_list:
        existing_addresses = user.addresses.all()  # Get existing addresses by ID

        for address_data in address_list:
            address_id = address_data.get("id")

            if address_id and address_id in existing_addresses:  # Update existing address
                address_instance = existing_addresses[address_id]
                for key, value in address_data.items():
                    setattr(address_instance, key, value)
                address_instance.save()

            else:  # Create new address
                # Address.objects.create(user=user, **address_data)
                address = address_create(user=user,
                               title=address_data.get('title'),
                               type=address_data.get('type'),
                               is_default=address_data.get('is_default'),
                               zip=address_data.get('zip'),
                               city=address_data.get('city'),
                               state=address_data.get('state'),
                               country=address_data.get('country'),
                               street_address=address_data.get('street_address'),
                               )

        # Optionally, delete addresses not in the provided list
        # existing_address_ids = {addr["id"] for addr in address_list if "id" in addr}
        # user.addresses.exclude(id__in=existing_address_ids).delete()

    # ... some additional tasks with the user ...

    return user
