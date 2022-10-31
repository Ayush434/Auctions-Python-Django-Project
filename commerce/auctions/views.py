import re
from tkinter import Widget
from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Bids, User, Auction, WatchList, Winner, Comments

# this helps to query data which might not exist yet in the database
from annoying.functions import get_object_or_None


# Gets data for all products and display them
def index(request):
    return render(request, "auctions/index.html",{
        "auction": Auction.objects.all(),
        "watchlist": WatchList.objects.all()
    })


# Displays all the categories
def categories(request):
    
    catlist = Auction.objects.all().values_list('category', flat=True)

    return render(request, "auctions/categories.html",{
        "catlist": set(catlist)
        
    })

# Input is the category name which is used to query all the products with that specific category and display them
def showCategory(request, name):
    
    user = request.user.username
    
    auction = Auction.objects.filter(category=name)
    
    present = False
    items = []
    
    if auction:    
        present = True
        
        return render(request, "auctions/category.html",{
            "auction": auction,
            "category": name,
            "present": present
        })
        
    else:
        # If no listing avaialble under this category
        
        return render(request, "auctions/category.html",{
            "present": False,
            "category": name,
        })

# Displays the closed listings and who sell / won them
def closed(request):
    
    winners = Winner.objects.all()
    empty = False
    
    if len(winners) == 0:
        empty = True

    return render(request, "auctions/closed.html",{
        "winners": winners,
        "empty": empty
    })


# Close the listing using specific listing ID
def closeListing(request, clID):
        
    obj = get_object_or_None(Bids, listingID=clID)
    listing = get_object_or_None(Auction, id=clID)
    
    # If listing not found that means it has been closed already
    if not listing:
        
        winners = Winner.objects.get(listingId=clID)
        empty = False
        print(winners)
        
        
        return render(request, "auctions/closedListing.html",{
            "winner": winners
        })
        
    # if listing is not closed, then grab the listing 
    listing = Auction.objects.get(pk=clID)
    winObj = Winner()
    
    # if there are no bids then that means user itself is the winner
    if not obj:
        winObj.listingId = clID
        winObj.owner = request.user.username
        winObj.winner = request.user.username
        winObj.winnerPrice = listing.bid
        winObj.title = listing.title
        
        winObj.save()    
    else:
        
        # if there are bids then find the user who won 
        bidObj = Bids.objects.get(listingID=clID)
        
        winObj.listingId = clID
        winObj.owner = request.user.username
        winObj.winner = bidObj.user
        winObj.winnerPrice = bidObj.newBid
        winObj.title = listing.title
        
        winObj.save()
        message = "Bid closed"
        
        bidObj.delete()
        
    # after collecting all the usefull info and adding it to Winner model, we can delete rest of the data related to the listing
    watchObj = WatchList.objects.filter(listingId=clID)
    if watchObj:
        watchObj.delete()
        
    comments = Comments.objects.filter(listingId=clID)
    
    if comments:
        comments.delete()
    
    
    listing.delete()
    
    return HttpResponseRedirect(reverse("closed"))
    
        
   

    
class CommentsForm(forms.Form):
    comment = forms.CharField(max_length=150)


class BidForm(forms.Form):
    bid = forms.DecimalField()


# Displays all details about the specific listing using ListingID
def showListing(request, item_id):
    
    # If the user submitted the bid
    if request.method == "POST":
        
        form = BidForm(request.POST)
        
        if form.is_valid():
            
            bid = form.cleaned_data["bid"]        
                                       
            item = Auction.objects.get(pk=item_id)
            
            # check if the bid is higher than the last bid
            if item.bid >= bid:
                
                
                comments = Comments.objects.filter(listingId=item_id)

                product = Auction.objects.get(pk=item_id)
                added = WatchList.objects.filter(listingId=item_id, user=request.user.username)
                
                error = f"Your bid is too small, please enter the bid higher than {item.bid}"
                return render(request, "auctions/showListing.html",{
                    "item": product,
                    "watchlist": added,
                    "bidForm": form,
                    "error": error,                
                    "commentsForm": CommentsForm(),
                    "comments": comments
                })
            
            # save the new bid 
            item.bid = bid
            item.save()
            
            bidObj = Bids.objects.filter(listingID=item_id)
            
            # if the bid already exists than delete that bid and add new "Higher" bid with new details of user
            if bidObj:
                bidObj.delete()            
            
            obj = Bids.objects.create(listingID=item.id, 
                                    title=item.title,
                                    newBid=bid,
                                    user=request.user.username)
            obj.save()
            # 
            
            comments = Comments.objects.filter(listingId=item_id)
            product = Auction.objects.get(pk=item_id)
            added = WatchList.objects.filter(listingId=item_id, user=request.user.username)
            
            success = "Your bid is added"
            return render(request, "auctions/showListing.html",{
                "item": product,
                "watchlist": added,
                "bidForm": BidForm(),
                "success": success,                
                "commentsForm": CommentsForm(),
                "comments": comments
            })
        
        else:
            
            # if the form validation fails, show the error to the user
            
            user=request.user.username
            comments = Comments.objects.filter(listingId=item_id)
            product = Auction.objects.get(pk=item_id)
            added = WatchList.objects.filter(listingId=item_id, user=user)
            
                
            return render(request, "auctions/showListing.html",{
                "item": product,
                "watchlist": added,
                "bidForm": form,
                "commentsForm": CommentsForm(),
                "comments": comments
            })
            
    else:
        
        # if the user arrives on the page first time
                    
        user=request.user.username
        comments = Comments.objects.filter(listingId=item_id)
        product = Auction.objects.get(pk=item_id)
        added = WatchList.objects.filter(listingId=item_id, user=user)
        
            
        return render(request, "auctions/showListing.html",{
            "item": product,
            "watchlist": added,
            "bidForm": BidForm(),
            "commentsForm": CommentsForm(),
            "comments": comments
        })
        

class CommentsForm(forms.Form):
    comment = forms.CharField(max_length=150)
    

# Adds the comment of the user to the listing    
def addComments(request, item_id):
    
    
    if request.method == "POST":
        
        form = CommentsForm(request.POST)
        user = request.user.username
        if form.is_valid():
            
            comment = form.cleaned_data["comment"]         
            
            obj = Comments()
            
            obj.comment = comment
            obj.user = user
            obj.listingId = item_id
            obj.save()
    
            comments = Comments.objects.filter(listingId=item_id)
            product = Auction.objects.get(pk=item_id)
            added = WatchList.objects.filter(listingId=item_id, user=user)
            
                
            return render(request, "auctions/showListing.html",{
                "item": product,
                "watchlist": added,
                "bidForm": BidForm(),
                "commentsForm": CommentsForm(),
                "comments": comments
            })
            
            
        else:
            
            comments = Comments.objects.filter(listingId=item_id)
            product = Auction.objects.get(pk=item_id)
            added = WatchList.objects.filter(listingId=item_id, user=user)
            return render(request, "auctions/showListing.html",{
                "item": product,
                "watchlist": added,
                "bidForm": BidForm(),
                "commentsForm": form,                
                "comments": comments
            })
    
    
    


# Displays the item that user has added to its watchlist
def watchList(request):
    
    user = request.user.username
    
    watchlist = WatchList.objects.filter(user=user)
    
    present = False
    items = []
    
    if watchlist:
        
        present = True
    
    
        for item in watchlist:
            
            each_item = Auction.objects.get(pk=item.listingId)
            items.append(each_item)
            
        print(items)
           
    
        return render(request, "auctions/watchList.html",{
            "auction": items,
            "present": present
        })
        
    else:
        return render(request, "auctions/watchList.html",{
            "present": False
        })


# adds the item to the user watchlist
def addToWatchlist(request, itemID):
    
    user = request.user.username
    
    obj = WatchList.objects.filter(user=user,listingId=itemID)
    print(obj)
    if obj:
        obj.delete()
        
        comments = Comments.objects.filter(listingId=itemID)
        product = Auction.objects.get(pk=itemID)
        added = WatchList.objects.filter(listingId=itemID, user=user)
        return render(request, "auctions/showListing.html",{
            "item": product,
            "watchlist": added,
            "bidForm": BidForm(),
            "commentsForm": CommentsForm(),                
            "comments": comments
        })
        
    else:
        obj = WatchList()
        obj.user = user
        obj.listingId = itemID
        obj.save()
        
        comments = Comments.objects.filter(listingId=itemID)
        product = Auction.objects.get(pk=itemID)
        added = WatchList.objects.filter(listingId=itemID, user=user)
        return render(request, "auctions/showListing.html",{
            "item": product,
            "watchlist": added,
            "bidForm": BidForm(),
            "commentsForm": CommentsForm(),                
            "comments": comments
        })
        

class newListingForm(forms.Form):
    title = forms.CharField(label = "Title")
    description = forms.CharField(widget=forms.Textarea, label="Description")
    bid = forms.DecimalField()
    image = forms.ImageField(required=False)
    category = forms.CharField(max_length=15)
    

# Creates the listing
def create(request):
    
    
    if request.method == "POST":
        # form = AuctionForm(request.POST)
        form = newListingForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            # obj = Auction()
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            bid = form.cleaned_data["bid"]
            image = form.cleaned_data.get("image")
            category = form.cleaned_data["category"]
            seller = request.user.username
            
            
            obj = Auction.objects.create(title=title,
                                         description=description,
                                         bid=bid,
                                         image=image,
                                         category=category,
                                         seller=seller)
            obj.save()
             
            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "auctions/createListing.html",{
                "form":form
            })
    
    
    return render(request, "auctions/createListing.html",{
        "form": newListingForm()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
