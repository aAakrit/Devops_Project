from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import  dashboard, registeration

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', registeration, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='dashboard'),
    path('trip/', views.trip_list, name='trip_list'),
    path('trip/create/', views.create_trip, name='create_trip'),
    path('send_request/', views.send_request, name='send_request'),
    path('trip/<int:trip_id>/', views.trip_details, name='trip_details'),
    path('trip/<int:trip_id>/update/', views.update_trip, name='update_trip'),
    path('trip/<int:trip_id>/delete/', views.delete_trip, name='delete_trip'),
    path('search_trip/', views.search_trip, name='search_trip'),
    path('get_results/', views.get_results, name='get_results'),
    path('search_results/', views.search_results, name='search_results'),
    path('request_success/', views.request_success, name='request_success'),
    path('send_request/', views.send_request, name='send_request'),
    path('received_requests/', views.received_requests, name='received_requests'),
]
