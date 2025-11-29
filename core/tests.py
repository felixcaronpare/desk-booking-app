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
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)

    def test_book_desk(self):
        self.client.login(username='user1', password='password')
        response = self.client.post(f'/book/{self.desk1.id}/', {'date': self.today})
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.assertTrue(Booking.objects.filter(user=self.user1, desk=self.desk1, date=self.today).exists())

    def test_double_booking_prevention_same_user(self):
        self.client.login(username='user1', password='password')
        # Book first desk
        self.client.post(f'/book/{self.desk1.id}/', {'date': self.today})
        # Try to book second desk
        response = self.client.post(f'/book/{self.desk2.id}/', {'date': self.today})
        # Should fail (redirect with error message, but we check DB)
        self.assertFalse(Booking.objects.filter(user=self.user1, desk=self.desk2, date=self.today).exists())

    def test_double_booking_prevention_same_desk(self):
        self.client.login(username='user1', password='password')
        self.client.post(f'/book/{self.desk1.id}/', {'date': self.today})
        self.client.logout()

        self.client.login(username='user2', password='password')
        response = self.client.post(f'/book/{self.desk1.id}/', {'date': self.today})
        # Should fail
        self.assertFalse(Booking.objects.filter(user=self.user2, desk=self.desk1, date=self.today).exists())

    def test_unbook_desk(self):
        self.client.login(username='user1', password='password')
        self.client.post(f'/book/{self.desk1.id}/', {'date': self.today})
        booking = Booking.objects.get(user=self.user1, desk=self.desk1, date=self.today)
        
        response = self.client.post(f'/unbook/{booking.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(id=booking.id).exists())

    def test_floor_plan_view(self):
        self.client.login(username='user1', password='password')
        response = self.client.get('/floor_plan/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Desk 1')
