from typing import Optional

from django.db.models import QuerySet

from common.utils import get_object
from layouts.models import FAQ, TermsAndConditions


def faq_list(*, filters=None) -> QuerySet[FAQ]:
    filters = filters or {}

    qs = FAQ.objects.all()

    return qs


def faq_get_by_slug(slug) -> Optional[FAQ]:
    faq = get_object(FAQ, slug=slug)

    return faq


def faq_get(faq_id) -> Optional[FAQ]:
    faq = get_object(FAQ, id=faq_id)

    return faq


def terms_and_conditions_list(*, filters=None) -> QuerySet[TermsAndConditions]:
    filters = filters or {}

    qs = TermsAndConditions.objects.all()

    return qs


def terms_and_conditions_get_by_slug(slug) -> Optional[TermsAndConditions]:
    terms_and_condition = get_object(TermsAndConditions, slug=slug)

    return terms_and_condition


def terms_and_conditions_get(terms_and_condition_id) -> Optional[TermsAndConditions]:
    terms_and_condition = get_object(TermsAndConditions, id=terms_and_condition_id)

    return terms_and_condition
