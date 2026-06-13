from django.db import models
from django.conf import settings  


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New Lead'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted'),
    ]

    
    
    LEAD_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('hot', 'Hot Lead'),
        ('followup', 'Follow-up'),
    ]

    title = models.CharField(max_length=255)
    source = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    lead_type = models.CharField(max_length=20, choices=LEAD_TYPE_CHOICES, default='normal')
    
    # 2. 'User' ki jagah settings.AUTH_USER_MODEL use karein
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='leads'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_leads'
    )
    
    ai_score = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TimelineGrowth(models.Model):
    date_label = models.CharField(max_length=50) 
    leads_count = models.IntegerField(default=0)

    def __str__(self):
        return self.date_label