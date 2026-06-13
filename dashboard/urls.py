from django.urls import path
from .views import DashboardMetricsView,LeadDashboardView

urlpatterns = [
    path('metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('lead-dashboard/', LeadDashboardView.as_view(), name='lead-dashboard'),
    
]