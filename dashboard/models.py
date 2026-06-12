from django.db import models


class Lead(models.Model):
    STATUS_CHOICES = [
        ('New', 'New Lead'),
        ('Contacted', 'Contacted'),
        ('Qualified', 'Qualified'),
        ('Proposal', 'Proposal'),
        ('Negotiation', 'Negotiation'),
        ('Won', 'Won'),
    ]
    SOURCE_CHOICES = [
        ('Meta Ads', 'Meta Ads'),
        ('Google Ads', 'Google Ads'),
        ('Website', 'Website'),
        ('WhatsApp', 'WhatsApp'),
        ('Referral', 'Referral'),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='New')
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='Website')
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

class TimelineGrowth(models.Model):
    date_label = models.CharField(max_length=50) 
    leads_count = models.IntegerField(default=0)

    def __str__(self):
        return self.date_label