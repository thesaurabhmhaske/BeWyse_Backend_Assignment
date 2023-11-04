# accounts/models.py
from djongo import models

class User(models.Model):
    _id = models.ObjectIdField()
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    additional_data = models.JSONField(default=dict)

    class Meta:
        db_table = 'root'

    def __str__(self):
        return self.username
