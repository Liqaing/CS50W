from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=64)
    
    def __str__(self):
        return f"Category name: {self.category_name}"
    
    @classmethod
    def get_other_category_pk(category):
        other_category, created = category.objects.get_or_create(category_name = "Other")
        return other_category.pk

class item(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.IntegerField()
    image_url = models.URLField(max_length=255, blank=True)
    owner = models.ForeignKey(User, related_name="items", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, related_name="winning_item", null=True, default=None, on_delete=models.CASCADE)
    categories = models.ForeignKey(Category, related_name="items", default=Category.get_other_category_pk, on_delete=models.CASCADE)

    def __str__(self):
        return f"Item ID {self.id}: {self.title}"
    
class bid(models.Model):
    bid = models.IntegerField()
    bid_item = models.ForeignKey(item, related_name="bids", on_delete=models.CASCADE)
    bid_user = models.ForeignKey(User, related_name="bids_item", on_delete=models.CASCADE)

    def __str__(self):
        return f"Bid ID: {self.id}, {self.bid_item} was bid at {self.bid}"

class comment(models.Model):
    comment = models.TextField()
    item = models.ForeignKey(item, related_name="comments", on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Item: {self.item}, User: {self.commenter}, Comment: {self.comment}"
    
# Tide user and item that they put to watchlist
class watchlist(models.Model):
    item = models.ForeignKey(item, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        # Define unique attribute, so combine between items id and user should be unique
        unique_together = ('item', 'user')
