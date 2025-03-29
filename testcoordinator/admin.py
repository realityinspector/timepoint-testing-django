from django.contrib import admin
from .models import TestCase, TestQueue, TestResult


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'endpoint_url', 'created_by', 'created_at', 'run_count')
    list_filter = ('status', 'created_by', 'created_at')
    search_fields = ('name', 'description', 'endpoint_url')
    readonly_fields = ('run_count', 'last_run', 'created_at', 'updated_at')


@admin.register(TestQueue)
class TestQueueAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_by', 'created_at', 'scheduled_time')
    list_filter = ('status', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('test_cases',)
    

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('test_case', 'status', 'run_at', 'response_time_ms')
    list_filter = ('status', 'run_at')
    search_fields = ('test_case__name',)
    readonly_fields = ('test_case', 'queue', 'run_at', 'status', 'response_data', 'response_time_ms') 