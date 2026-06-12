from django.urls import path
from .views import LoginView, RegisterView, ForgotPasswordView, ResetPasswordConfirmView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'), # 🆕 न्यू एंडपॉइंट
]