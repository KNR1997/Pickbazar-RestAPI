from django.urls import path

from layouts.apis import faq_apis, term_and_condition_apis

urlpatterns = [
    path('faqs/', faq_apis.FaqListApi.as_view()),
    path('faqs/create', faq_apis.FaqCreateApi.as_view()),
    path('faqs/<str:slug>', faq_apis.FaqDetailApi.as_view()),
    path('faqs/<str:faq_id>/update', faq_apis.FaqUpdateApi.as_view()),
    path('faqs/<str:faq_id>/delete', faq_apis.FaqDeleteApi.as_view()),

    path('terms-and-conditions/', term_and_condition_apis.TermsAndConditionListApi.as_view()),
    path('terms-and-conditions/create', term_and_condition_apis.TermsAndConditionCreateApi.as_view()),
    path('terms-and-conditions/<str:slug>', term_and_condition_apis.TermsAndConditionDetailApi.as_view()),
    path('terms-and-conditions/<str:terms_and_condition_id>/update', term_and_condition_apis.TermsAndConditionUpdateApi.as_view()),
    path('terms-and-conditions/<str:terms_and_condition_id>/delete', term_and_condition_apis.TermsAndConditionDeleteApi.as_view()),
]
