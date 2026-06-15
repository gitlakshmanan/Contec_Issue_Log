from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    
    class Meta:
        ordering = ['completed', '-priority', 'due_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return timezone.now() > self.due_date
        return False