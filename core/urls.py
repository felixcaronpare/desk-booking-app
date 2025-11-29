from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('floor_plan'), name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('floor_plan/', views.floor_plan, name='floor_plan'),
    path('book/<int:desk_id>/', views.book_desk, name='book_desk'),
    path('unbook/<int:booking_id>/', views.unbook_desk, name='unbook_desk'),
]
