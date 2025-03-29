from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TestCase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    endpoint_url = models.URLField()
    payload = models.JSONField(default=dict, blank=True)
    expected_response = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    run_count = models.IntegerField(default=0)
    last_run = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def mark_as_running(self):
        self.status = 'running'
        self.last_run = timezone.now()
        self.run_count += 1
        self.save()
        
    def mark_as_complete(self, status, result=None):
        self.status = status
        if result:
            self.result_data = result
        self.save()


class TestQueue(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    test_cases = models.ManyToManyField(TestCase, related_name='queues')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_queues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class TestResult(models.Model):
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='results')
    queue = models.ForeignKey(TestQueue, on_delete=models.CASCADE, related_name='results', null=True, blank=True)
    run_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=TestCase.STATUS_CHOICES)
    response_data = models.JSONField(default=dict, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Result for {self.test_case.name} - {self.status}" 