from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from . import util 

from .models import User, Listing, Followed, Bid, Comment


def index(request):
    if request.method == 'POST':
        # Accessing the data
        owner = request.user
        title = request.POST.get('title')
        description = request.POST.get('description')
        bid = request.POST.get('bid')
        category = request.POST.get('category')
        image_url = request.POST.get('image')

        # if all the necessary data is present, save the listing 
        if not title or not description or not bid or not category:
            return render(request, 'auctions/create.html')
        new_listing = Listing(owner=owner, title=title, description=description, category=category, image_url=image_url, price=bid)
        new_listing.save()
 
        return redirect('index')
    
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.all(),
        'watchlist_filter': False,
        'categories_filter': False
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = util.cut_spaces(request.POST["username"])
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
        username = util.cut_spaces(request.POST["username"])
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if username == '' or email == '' or password == '' or confirmation == '':
            return render(request, "auctions/register.html", {
                "message": "Please fill out all fields."
            })
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        if len(password) < 8:
            return render(request, "auctions/register.html", {
                "message": "The password must be at least 8 characters long."
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


def create(request):
    return render(request, 'auctions/create.html')


def categories(request):
    all_categories = Listing.category_choices  
    return render(request, 'auctions/categories.html', {
        'categories': all_categories
    })

def category(request, value):
    listings = Listing.objects.filter(category=value)
    return render(request, "auctions/index.html", {
        'listings': listings,
        'categories_filter': True,
        'category': value.capitalize()
    })

def view_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)   # the listing 
    bids = listing.bids.all()                      # all the listing's bids
    num_bids = listing.bids.count()                # the number of all bids
    highest_bid = bids.order_by('-value').first()
    current_user = request.user                    # the current client 
    in_watchlist = False
    comments = listing.comments.all()

    # if the user is not authenticated, he is a buyer 
    if current_user.is_authenticated:
        # Checking if the current client is a buyer or the owner of the listing 
        if listing.owner == current_user:              
            buyer = False
        else: 
            buyer = True
        # Checking if the listing is in the user's watchlist 
        in_watchlist = current_user.watchlist.filter(item=listing).exists()
    else:
        buyer = True
    
    # If listing ended, save a winner message
    if listing.ended:
        if not highest_bid:
            end_message = 'Auction closed.'
        else:
            winner = highest_bid.bidder             # accessing the winner user
            if winner == current_user:
                end_message = f'Auction closed. Congratulations for winning with the bid of { highest_bid.value }$!'
            else:
                end_message = f'Auction closed. Congratulations to { winner } for winning with the bid of { highest_bid.value }$!'
    else:
        end_message = ''
        if highest_bid:
            highest_bid = highest_bid.value
        
    return render(request, 'auctions/view_listing.html', {
        'listing': listing,
        'bids': bids,
        'comments': comments,
        'buyer': buyer,
        'current_user': current_user,
        'highest_bid': highest_bid,
        'num_bids': num_bids,
        'in_watchlist': in_watchlist,
        'end_message': end_message
    })

def watchlist_add(request, listing_id):
    current_user = request.user
    listing = Listing.objects.get(pk=listing_id)
    # Checking if the user is authenticated or not
    if current_user.is_authenticated:
        # if the item already in watchlist, just return to the view page
        if Followed.objects.filter(user=current_user, item=listing).exists():
            return redirect('view', listing_id=listing_id)
        # else save the item in the watchlist and return 
        new_followed = Followed(user=current_user, item=listing)
        new_followed.save()
        return redirect('view', listing_id=listing_id)
    # If not, go to login 
    return redirect('login')


def watchlist_delete(request, listing_id):
    current_user = request.user 
    listing = Listing.objects.get(pk=listing_id)
    # Checking if the user is authenticated or not (they should be at this stage, just a error defense mechanism)
    if current_user.is_authenticated:
        # If the object exists, delete it from Followed 
        followed = Followed.objects.filter(user=current_user, item=listing)
        if followed.exists():  
            followed.delete()
        return redirect('view', listing_id=listing_id)
    
    return redirect('login')
        
def watchlist(request):
    user = request.user
    watchlist_listings = [followed.item for followed in user.watchlist.all()]  # a list of all user's watchlist listings  
    return render(request, "auctions/index.html", {
        'listings': watchlist_listings,
        'watchlist_filter': True
    })

def bid(request, listing_id):
    bidder = request.user

    if not bidder.is_authenticated:
        return redirect('index')
    # gather the bid, listing object, the list of all bids associated with the listing, and the highest bid on the listing from all bids. 
    if request.method == 'POST':
        bid = request.POST.get('bid')
        listing = Listing.objects.get(pk=listing_id)
        all_bids = listing.bids.all()
        highest_bid = all_bids.order_by('-value').first()

        if not bid:
            messages.error(request, 'Please enter your bid.')
            return redirect('view', listing_id=listing_id)
        if int(bid) < listing.price:
            messages.error(request, 'Your bid must be higher than the price.')
            return redirect('view', listing_id=listing_id)
        if highest_bid and int(bid) <= highest_bid.value:
            messages.error(request, 'Your bid must be higher than the current highest one.')
            return redirect('view', listing_id=listing_id)
        
        new_bid = Bid(listing=listing, bidder=bidder, value=bid)
        new_bid.save()
        messages.success(request, 'Bid placed successfully.')
        return redirect('add', listing_id=listing_id)

def close(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    listing.ended = True        # removing from active listings
    listing.save()              # save the changes 
    return redirect('view', listing_id=listing_id)

def comment(request, listing_id):
    current_user = request.user
    if not current_user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        text = util.cut_spaces(request.POST.get('text'))
        if not text:
            return redirect('view', listing_id=listing_id)
        new_comment = Comment(listing=listing, commentator=current_user, text=text)
        new_comment.save()
        return redirect('view', listing_id=listing_id)






    
        

        


