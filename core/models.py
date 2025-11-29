from django.db import models
from django.contrib.auth.models import User

class Desk(models.Model):
    name = models.CharField(max_length=100)
    row = models.IntegerField(default=0)
    col = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Row: {self.row}, Col: {self.col})"


class Booking(models.Model):
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} → {self.desk} on {self.date}"
