from django.db import models
import uuid

class User(models.Model): # basic for now
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    # email = models.CharField(max_length=100)
    # phoneNumber = models.CharField(max_length=100)
    # userName = models.CharField(max_length=100)
    # passWord = models.CharField(max_length=100)
    # address = models.CharField(max_length=100)

    def str(self):
        return self.name

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class Lab(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)