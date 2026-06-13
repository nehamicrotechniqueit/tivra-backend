from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from dashboard.models import Lead
from rest_framework.permissions import AllowAny 
from django.db.models import Count


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
    


class LeadDashboardView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        # Jab AllowAny hoga, toh request.user anonymous ho sakta hai, 
        # isliye testing ke liye hum thoda dummy ya direct user fallback de dete hain
        user = request.user if request.user.is_authenticated else None
        
        metrics = Lead.objects.aggregate(
            total_leads=Count('id'),
            new_leads=Count('id', filter=Q(status='new')),
            contacted=Count('id', filter=Q(status='contacted')),
            qualified=Count('id', filter=Q(status='qualified')),
            converted=Count('id', filter=Q(status='converted'))
        )

        all_leads = Lead.objects.all().values()
        my_leads = Lead.objects.filter(created_by=user).values() if user else all_leads
        unassigned_leads = Lead.objects.filter(assigned_to__isnull=True).values()
        followups = Lead.objects.filter(lead_type='followup').values()
        hot_leads = Lead.objects.filter(lead_type='hot').values()

        return Response({
            "metrics": metrics,
            "tabsData": {
                "allLeads": list(all_leads),
                "myLeads": list(my_leads),
                "unassigned": list(unassigned_leads),
                "followups": list(followups),
                "hotLeads": list(hot_leads),
            }
        })