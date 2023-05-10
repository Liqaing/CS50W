from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction_Listings(models.Model):
    title = models.CharField(max_length=64)
    describtion = models.TextField()
    image_url = models.URLField(max_length=255)