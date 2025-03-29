from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Onboarding wizard
    path('onboarding/', views.OnboardingWizardView.as_view(), name='onboarding_wizard'),
    
    # Test Cases
    path('testcases/', views.TestCaseListView.as_view(), name='test_case_list'),
    path('testcases/new/', views.TestCaseCreateView.as_view(), name='test_case_create'),
    path('testcases/<int:pk>/', views.TestCaseDetailView.as_view(), name='test_case_detail'),
    path('testcases/<int:pk>/edit/', views.TestCaseUpdateView.as_view(), name='test_case_update'),
    path('testcases/<int:pk>/delete/', views.TestCaseDeleteView.as_view(), name='test_case_delete'),
    path('testcases/<int:pk>/run/', views.run_test_case, name='run_test_case'),
    
    # Test Queues
    path('testqueues/', views.TestQueueListView.as_view(), name='test_queue_list'),
    path('testqueues/new/', views.TestQueueCreateView.as_view(), name='test_queue_create'),
    path('testqueues/<int:pk>/', views.TestQueueDetailView.as_view(), name='test_queue_detail'),
    path('testqueues/<int:pk>/edit/', views.TestQueueUpdateView.as_view(), name='test_queue_update'),
    path('testqueues/<int:pk>/delete/', views.TestQueueDeleteView.as_view(), name='test_queue_delete'),
    path('testqueues/<int:pk>/run/', views.run_test_queue, name='run_test_queue'),
    
    # Authentication
    path('login/', LoginView.as_view(template_name='testcoordinator/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
] 