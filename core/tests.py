from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Desk, Booking
from django.utils import timezone
from datetime import timedelta

class BookingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.desk1 = Desk.objects.create(name='Desk 1', row=0, col=0)
        self.desk2 = Desk.objects.create(name='Desk 2', row=0, col=1)
        
        # Calculate a valid workday (Monday of current week)
        today = timezone.now().date()
        self.monday = today - timedelta(days=today.weekday())
        self.friday = self.monday + timedelta(days=4)
        self.next_monday = self.monday + timedelta(days=7)
        self.last_sunday = self.monday - timedelta(days=1)

    def test_book_desk_valid_day(self):
        self.client.login(username='user1', password='password')
        response = self.client.post(f'/book/{self.desk1.id}/', {'date': self.monday})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(user=self.user1, desk=self.desk1, date=self.monday).exists())

    def test_book_desk_invalid_day_next_week(self):
        self.client.login(username='user1', password='password')
        response = self.client.post(f'/book/{self.desk1.id}/', {'date': self.next_monday})
        # Should fail/redirect without booking
        self.assertFalse(Booking.objects.filter(user=self.user1, desk=self.desk1, date=self.next_monday).exists())

    def test_book_desk_invalid_day_last_week(self):
        self.client.login(username='user1', password='password')
        response = self.client.post(f'/book/{self.desk1.id}/', {'date': self.last_sunday})
        # Should fail/redirect without booking
        self.assertFalse(Booking.objects.filter(user=self.user1, desk=self.desk1, date=self.last_sunday).exists())

    def test_double_booking_prevention_same_user(self):
        self.client.login(username='user1', password='password')
        self.client.post(f'/book/{self.desk1.id}/', {'date': self.monday})
        self.client.post(f'/book/{self.desk2.id}/', {'date': self.monday})
        self.assertFalse(Booking.objects.filter(user=self.user1, desk=self.desk2, date=self.monday).exists())

    def test_double_booking_prevention_same_desk(self):
        self.client.login(username='user1', password='password')
        self.client.post(f'/book/{self.desk1.id}/', {'date': self.monday})
        self.client.logout()

        self.client.login(username='user2', password='password')
        self.client.post(f'/book/{self.desk1.id}/', {'date': self.monday})
        self.assertFalse(Booking.objects.filter(user=self.user2, desk=self.desk1, date=self.monday).exists())

    def test_unbook_desk(self):
        self.client.login(username='user1', password='password')
        self.client.post(f'/book/{self.desk1.id}/', {'date': self.monday})
        booking = Booking.objects.get(user=self.user1, desk=self.desk1, date=self.monday)
        
        response = self.client.post(f'/unbook/{booking.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(id=booking.id).exists())

    def test_floor_plan_view(self):
        self.client.login(username='user1', password='password')
        response = self.client.get('/floor_plan/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Desk 1')
