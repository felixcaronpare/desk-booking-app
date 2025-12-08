from django.db import models
from django.contrib.auth.models import User

class Desk(models.Model):
    number = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name} (X: {self.x}, Y: {self.y}) ({self.number})"


class Booking(models.Model):
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} → {self.desk} on {self.date}"
