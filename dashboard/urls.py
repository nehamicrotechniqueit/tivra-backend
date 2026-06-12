from django.urls import path
from .views import DashboardAPIView

urlpatterns = [
    path('metrics/', DashboardAPIView.as_view(), name='dashboard-metrics'),
]