from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class item(models.Model):
    title = models.CharField(max_length=64)
    describtion = models.TextField()
    starting_bid = models.IntegerField()
    image_url = models.URLField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Item ID {self.id}: {self.title}"
    
class bid(models.Model):
    bid = models.IntegerField()
    bid_item = models.ForeignKey(item, related_name="bids", on_delete=models.CASCADE)

    def __str__(self):
        return f"Bid ID {self.id}: Item: {self.bid_item} bid at {self.bid}"

class comment(models.Model):
    comment = models.TextField()
    item = models.ForeignKey(item, related_name="comments", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Item: {self.item}, Comment: {self.comment}"