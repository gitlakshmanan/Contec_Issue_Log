from django.urls import path
from .views import (
    TaskList, TaskDetail, TaskCreate, TaskUpdate, TaskDeleteView, CustomLoginView, 
    RegisterPage, TaskReorder, IssueList, IssueDetail, IssueCreate, IssueUpdate, 
    IssueDelete, ClosedIssuesList, close_issue, reopen_issue, export_issues_csv, 
    import_issues_csv, send_email_popup, issue_statistics, dashboard,
    download_template_csv,
    user_management, approve_user, user_profile, pending_approval, welcome, custom_logout, 
    reset_user_password, delete_user, toggle_tips_preference
)

# metrics_api imported below to avoid import cycle issues
from .views import metrics_api

urlpatterns = [
    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),

    # Root URL and dashboard both render the welcome/dashboard homepage
    path('', welcome, name='home'),

    # Dashboard (same as home)
    path('dashboard/', welcome, name='dashboard'),

    # Task URLs (keeping for backward compatibility)
    path('tasks/', TaskList.as_view(), name='tasks'),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task'),
    path('task-create/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', TaskDeleteView.as_view(), name='task-delete'),
    path('task-reorder/', TaskReorder.as_view(), name='task-reorder'),

    # Issue Management URLs
    path('issues/', IssueList.as_view(), name='issues'),
    path('issues/closed/', ClosedIssuesList.as_view(), name='closed-issues'),
    path('issue/<int:pk>/', IssueDetail.as_view(), name='issue-detail'),
    path('issue-create/', IssueCreate.as_view(), name='issue-create'),
    path('issue-update/<int:pk>/', IssueUpdate.as_view(), name='issue-update'),
    path('issue-delete/<int:pk>/', IssueDelete.as_view(), name='issue-delete'),
    path('issue/<int:issue_id>/close/', close_issue, name='close-issue'),
    path('issue/<int:issue_id>/reopen/', reopen_issue, name='reopen-issue'),
    
    # Import/Export URLs
    path('export-issues/', export_issues_csv, name='export-issues'),
    path('import-issues/', import_issues_csv, name='import-issues'),
    path('download-template/', download_template_csv, name='download-template'),
    
    # Email functionality
    path('issue/<int:issue_id>/email/', send_email_popup, name='issue-email'),
    path('preferences/toggle-tips/', toggle_tips_preference, name='toggle-tips'),
    
    # Statistics
    path('statistics/', issue_statistics, name='issue-statistics'),
    
    # User Management URLs
    path('users/', user_management, name='user-management'),
    path('users/<int:user_id>/approve/', approve_user, name='approve-user'),
    path('users/<int:user_id>/reset-password/', reset_user_password, name='reset-user-password'),
    path('users/<int:user_id>/delete/', delete_user, name='delete-user'),
    path('profile/', user_profile, name='user-profile'),
    path('pending-approval/', pending_approval, name='pending-approval'),
    path('rejected-user/', pending_approval, name='rejected-user'),  # Same view, different template
    path('welcome/', welcome, name='welcome'),
    path('api/metrics/', metrics_api, name='metrics_api'),
]
