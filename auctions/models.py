from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

# auction listings, bids, comments, and auction categories
# rememeber to makemigrations and migrate after you make changes to the database 

# required models: - auction listings f
#                  - bids
#                  - comments on auction listings
#                   AbstractUser --> has fields for username, email, password
#                   all own and watchlist listings


class User(AbstractUser):                   
    def __self__(self):                 
        return f'{self.username}'                 


class Listing(models.Model):
    category_choices = [
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'),
        ('sport', 'Sport'),
        ('clothing', 'Clothing'),
        ('health', 'Health'),
        ('miscellaneous', 'Miscellaneous')
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1024)
    category = models.CharField(max_length=64, choices=category_choices)
    image_url = models.CharField(max_length=128, blank=True)
    price = models.IntegerField()
    date = models.DateField(default=now)
    ended = models.BooleanField(default=False)


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids') # provided with a Listing instance listing, listing.bids.all() gets all Bid instances associated with listing
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')     # provided with a User instance user, user.bids.all() gets all Bid instances associated with user
    value = models.IntegerField()

class Followed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')   # provided with a User instance user, user.watchlist.all() gets all Followed instances associated with user
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='watchlist') # provided with a Listing instance listing, Listing.watchlist.all() gets all Followed instances associated with listing


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    commentator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.CharField(max_length=1024)
    date = models.DateField(default=now)
    



  