from django.urls import path
from . import views

urlpatterns = [
    path('floor_plan/', views.floor_plan, name='floor_plan'),
    path('book/<int:desk_id>/', views.book_desk, name='book_desk'),
    path('unbook/<int:booking_id>/', views.unbook_desk, name='unbook_desk'),
]
