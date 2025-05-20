from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import CustomTokenObtainPairView, LogoutView, RegisterView, CustomerTokenObtainPairView, \
    ChangePasswordView, UserRegistrationAPIView

urlpatterns = [
    path("api/register", UserRegistrationAPIView.as_view(), name="customer_register"),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="admin_login"),
    # path("api/login", CustomerTokenObtainPairView.as_view(), name="customer_login"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/logout", LogoutView.as_view(), name="logout"),
    path("api/change-password", ChangePasswordView.as_view(), name="logout"),

]
