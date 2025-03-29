import json
import requests
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from .models import TestCase, TestQueue, TestResult
from .forms import UserRegistrationForm


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'testcoordinator/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test_cases'] = TestCase.objects.all().order_by('-created_at')[:10]
        context['test_queues'] = TestQueue.objects.all().order_by('-created_at')[:5]
        context['recent_results'] = TestResult.objects.all().order_by('-run_at')[:10]
        
        # Count statistics
        context['stats'] = {
            'total_tests': TestCase.objects.count(),
            'pending_tests': TestCase.objects.filter(status='pending').count(),
            'passed_tests': TestCase.objects.filter(status='passed').count(),
            'failed_tests': TestCase.objects.filter(status='failed').count(),
        }
        return context


class OnboardingWizardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'testcoordinator/onboarding_wizard.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Any context needed for the onboarding steps
        return context


class TestCaseListView(LoginRequiredMixin, ListView):
    model = TestCase
    template_name = 'testcoordinator/testcase_list.html'
    context_object_name = 'test_cases'
    ordering = ['-created_at']


class TestCaseDetailView(LoginRequiredMixin, DetailView):
    model = TestCase
    template_name = 'testcoordinator/testcase_detail.html'
    context_object_name = 'test_case'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = self.object.results.all().order_by('-run_at')[:10]
        return context


class TestCaseCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TestCase
    template_name = 'testcoordinator/testcase_form.html'
    fields = ['name', 'description', 'endpoint_url', 'payload', 'expected_response']
    success_message = "Test case was created successfully"
    success_url = reverse_lazy('test_case_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TestCaseUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TestCase
    template_name = 'testcoordinator/testcase_form.html'
    fields = ['name', 'description', 'endpoint_url', 'payload', 'expected_response']
    success_message = "Test case was updated successfully"
    
    def get_success_url(self):
        return reverse_lazy('test_case_detail', kwargs={'pk': self.object.pk})


class TestCaseDeleteView(LoginRequiredMixin, DeleteView):
    model = TestCase
    template_name = 'testcoordinator/testcase_confirm_delete.html'
    success_url = reverse_lazy('test_case_list')
    success_message = "Test case was deleted successfully"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class TestQueueListView(LoginRequiredMixin, ListView):
    model = TestQueue
    template_name = 'testcoordinator/testqueue_list.html'
    context_object_name = 'test_queues'
    ordering = ['-created_at']


class TestQueueDetailView(LoginRequiredMixin, DetailView):
    model = TestQueue
    template_name = 'testcoordinator/testqueue_detail.html'
    context_object_name = 'test_queue'


class TestQueueCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TestQueue
    template_name = 'testcoordinator/testqueue_form.html'
    fields = ['name', 'description', 'test_cases', 'scheduled_time']
    success_message = "Test queue was created successfully"
    success_url = reverse_lazy('test_queue_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TestQueueUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TestQueue
    template_name = 'testcoordinator/testqueue_form.html'
    fields = ['name', 'description', 'test_cases', 'scheduled_time']
    success_message = "Test queue was updated successfully"
    
    def get_success_url(self):
        return reverse_lazy('test_queue_detail', kwargs={'pk': self.object.pk})


class TestQueueDeleteView(LoginRequiredMixin, DeleteView):
    model = TestQueue
    template_name = 'testcoordinator/testqueue_confirm_delete.html'
    success_url = reverse_lazy('test_queue_list')
    success_message = "Test queue was deleted successfully"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@login_required
def run_test_case(request, pk):
    test_case = get_object_or_404(TestCase, pk=pk)
    
    try:
        test_case.mark_as_running()
        
        # Record start time
        start_time = time.time()
        
        # Make the API request
        response = requests.post(
            test_case.endpoint_url,
            json=test_case.payload,
            headers={'Content-Type': 'application/json'},
            timeout=30  # Timeout after 30 seconds
        )
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Process response
        response_data = response.json() if response.status_code < 400 else {'error': response.text}
        
        # Determine test status based on response
        if response.status_code >= 400:
            status = 'error'
        else:
            # Compare expected response with actual response if expected is provided
            if test_case.expected_response:
                # Simple equality check - could be made more sophisticated
                if json.dumps(test_case.expected_response, sort_keys=True) == json.dumps(response_data, sort_keys=True):
                    status = 'passed'
                else:
                    status = 'failed'
            else:
                # If no expected response is specified, just check if API call succeeds
                status = 'passed' if response.status_code < 400 else 'failed'
        
        # Create test result
        result = TestResult.objects.create(
            test_case=test_case,
            status=status,
            response_data=response_data,
            response_time_ms=response_time_ms
        )
        
        # Update test case status
        test_case.mark_as_complete(status, result)
        
        messages.success(request, f"Test case '{test_case.name}' run completed with status: {status}")
        
    except Exception as e:
        # Handle any exceptions during test execution
        TestResult.objects.create(
            test_case=test_case,
            status='error',
            response_data={'error': str(e)},
        )
        test_case.mark_as_complete('error')
        messages.error(request, f"Error running test case: {str(e)}")
    
    return redirect('test_case_detail', pk=test_case.pk)


@login_required
def run_test_queue(request, pk):
    test_queue = get_object_or_404(TestQueue, pk=pk)
    test_queue.status = 'running'
    test_queue.save()
    
    # Get all test cases in the queue
    test_cases = test_queue.test_cases.all()
    
    for test_case in test_cases:
        try:
            test_case.mark_as_running()
            
            # Record start time
            start_time = time.time()
            
            # Make the API request
            response = requests.post(
                test_case.endpoint_url,
                json=test_case.payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Process response
            response_data = response.json() if response.status_code < 400 else {'error': response.text}
            
            # Determine test status
            if response.status_code >= 400:
                status = 'error'
            else:
                if test_case.expected_response:
                    if json.dumps(test_case.expected_response, sort_keys=True) == json.dumps(response_data, sort_keys=True):
                        status = 'passed'
                    else:
                        status = 'failed'
                else:
                    status = 'passed' if response.status_code < 400 else 'failed'
            
            # Create test result
            result = TestResult.objects.create(
                test_case=test_case,
                queue=test_queue,
                status=status,
                response_data=response_data,
                response_time_ms=response_time_ms
            )
            
            # Update test case status
            test_case.mark_as_complete(status, result)
            
        except Exception as e:
            # Handle any exceptions during test execution
            TestResult.objects.create(
                test_case=test_case,
                queue=test_queue,
                status='error',
                response_data={'error': str(e)},
            )
            test_case.mark_as_complete('error')
    
    # Update queue status
    test_queue.status = 'completed'
    test_queue.save()
    
    messages.success(request, f"Test queue '{test_queue.name}' run completed")
    return redirect('test_queue_detail', pk=test_queue.pk)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Test Coordinator.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'testcoordinator/register.html', {'form': form}) 