from django.urls import path

from systemconfig.apis import settings_apis

urlpatterns = [
    path('settings/',               settings_apis.SettingsDetailApi.as_view()),
    path('settings/update',         settings_apis.SettingsUpdateApi.as_view()),

    # path('attachments', file_upload_views.upload_file, name='upload_file'),
]
