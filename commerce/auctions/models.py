from email.policy import default
from typing_extensions import Required
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser, models.Model):
    pass



class Comments(models.Model):
    user = models.CharField(max_length=50,blank=True, null=True)
    comment = models.CharField(max_length=150,blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add = True)
    listingId = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"user is {self.user}. comment: {self.comment}  timestamp: {self.timestamp}"
    
    

class Auction(models.Model):
    
    title = models.CharField(max_length=50)
    description = models.TextField()
    bid = models.DecimalField(decimal_places=2, max_digits=55) 
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    category = models.CharField(max_length=15)
    seller = models.CharField(max_length=50,blank=True, null=True)

    
    def __str__(self):
        return f"Title is {self.title}. bid is {self.bid}.  Description: {self.description} and Category:  {self.category}"
    

class Bids(models.Model):
    
    title = models.CharField(max_length=60, blank=True)
    user = models.CharField(max_length=50,blank=True, null=True)
    newBid = models.DecimalField(decimal_places=2, max_digits=55, blank=True, null=True)
    listingID = models.IntegerField(blank=True, null=True)
    


    def __str__(self):
        return f"user is {self.user}. title: {self.title} and newBid:  {self.newBid}"
    
    
class WatchList(models.Model):
    user = models.CharField(max_length=50,blank=True, null=True)
    listingId = models.IntegerField(blank=True, null=True)

    def __str__(self):
            return f"user is {self.user}. listingId: {self.listingId}"
    

class Winner(models.Model):
    owner = models.CharField(max_length=50,blank=True, null=True)
    winner = models.CharField(max_length=50,blank=True, null=True)
    winnerPrice =  models.DecimalField(decimal_places=2, max_digits=55, blank=True, null=True)
    title = models.CharField(max_length=60, blank=True)
    listingId = models.IntegerField(blank=True, null=True)
    
    
    def __str__(self):
        return f"Title is {self.title}. owner: {self.owner}  winner:  {self.winner}, winnerPrice: {self.winnerPrice}"

