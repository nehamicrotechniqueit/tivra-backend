from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken


class DashboardMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Precise UI values mapped exactly from image_d6091c.jpg
        payload = {
            "kpis": {
                "total_leads": "25,689",
                "total_customers": "8,426",
                "whatsapp_sent": "1,28,934",
                "open_rate": "45.6%",
                "conversion_rate": "16.35%",
                "revenue": "2,45,80,900"
            },
            "lead_sources": [
                {"name": "Meta Ads", "percentage": 45.8, "color": "#2563EB"},
                {"name": "Google Ads", "percentage": 25.6, "color": "#0EA5E9"},
                {"name": "Website", "percentage": 15.2, "color": "#F59E0B"},
                {"name": "WhatsApp", "percentage": 8.7, "color": "#10B981"},
                {"name": "Referral", "percentage": 4.7, "color": "#64748B"}
            ],
            "sales_pipeline": {
                "new_leads": "25,689",
                "contacted": "16,324",
                "qualified": "9,125",
                "proposal": "4,928",
                "negotiation": "2,450",
                "won": "1,245"
            }
        }
        return Response(payload, status=status.HTTP_200_OK)