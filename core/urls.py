from django.urls import path
from . import views

app_name = 'core' 

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('mark_read/<int:doc_id>/', views.mark_read, name='mark_read'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('archive/', views.archive_view, name='archive'),
    path('mail/', views.internal_mail, name='internal_mail'),
    
    
    # مسارات الميزات الجديدة
    path('statistics/', views.statistics_view, name='statistics'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
]