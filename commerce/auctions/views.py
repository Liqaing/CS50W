from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

from .models import User, item, bid, comment, watchlist, Category


def index(request):

    # Get all listing from item table
    listings = list(item.objects.all().values())
    
    # Get the current price of each active item, which is its the highest value that was bid
    for listing in listings:
        # Get bid values from the bid table where its foreigh key = primary key of item table
        try:
            # Sort bid value in DESC order and get it first value (Which is the highest value)
            current_bid = bid.objects.filter(bid_item = listing["id"]).order_by("-bid").first()
        # Except any particular item doesn't have any bid yet
        except bid.DoesNotExist:
            current_bid = None

        # If current_bid is not none, then assign its value to that listing current bid
        if current_bid:
            listing["current_bid"] = current_bid.bid
    
        # Retrive category name from table
        listing["category"] = Category.objects.get(id = listing["categories_id"]).category_name

    return render(request, "auctions/index.html", {
        "listings": listings
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

@login_required(login_url="login")
def create_listing(request):
    if request.method == "POST":

        # Get all data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]
        category_id = request.POST.get("category")
        

        # Validate data that user submit
        error_dict = {}
        
        # Missing input field
        if not title:
            error_dict["missing_title"] = "Listing title is missing"
        if not description:
            error_dict["missing_description"] = "Listing description is missing"
        if not starting_bid:
            error_dict["missing_starting_bid"] = "Listing starting bid is missing"

        # Check category
        if category_id:
            category = Category.objects.get(id=category_id)
        
        # Validate starting bid
        try:
            starting_bid = int(starting_bid)
        except ValueError:
            error_dict["starting_bid_not_int"] = "Starting Bid need to be a number" 

        # Validate url of image_url, only validate when user input image url
        if image_url:
            validate_url = URLValidator() # create validator_url object from urlvalidator class 
            try:
                validate_url(image_url)
            except ValidationError:
                error_dict["invalid_image_url"] = "Invalid Url For Image"

        # Check if there is any error in user input
        if error_dict:
            return render(request, "auctions/create_listing.html", {
                "error": error_dict
            })

        # Create item object and add its to the item database
        owner = request.user
        new_item = item(title=title, description=description, categories=category, starting_bid=starting_bid, image_url=image_url, owner=owner)
        new_item.save()

        return HttpResponseRedirect(reverse("index"))

    # Retrive all categories
    categories = Category.objects.all()

    return render(request, "auctions/create_listing.html", {
        "categories": categories,
    })

def view_listing(request, id):

    # Retrive the item from database base on id from parameter (get() return object)
    listing = item.objects.get(id=id)

    # Retrive the current highest bid of the item from the bid table
    current_bid = bid.objects.filter(bid_item = listing.id).order_by("-bid").first()

    # Then assign it to new field of listing object (curent_bid is a query set return by filter)
    if current_bid:
        listing.current_bid = current_bid.bid
    # If there is not bid yet, other than starting bid
    else:
        listing.current_bid = None

    # Check if user is the owner of the listing
    if listing.owner.id == request.user.id:
        listing.is_owner = True
    else:
        listing.is_owner = False

    # Display all comment
    comments = comment.objects.filter(item_id = listing.id)
    if comments:
       listing.comment = comments
    else:
        listing.comment = None

    # On user request
    if request.method == "POST":
        
        # Add or remove watchlist
        if "watchlist" in request.POST:

            # User add listing item to their watchlist
            if request.POST["watchlist"] == "add_watchlist":

                # Retrive item instance from item table then pass it to watchlist table
                try:
                    add_watchlist = watchlist.objects.create(item=listing, user=request.user)
                    add_watchlist.save()

                # Except if this item is already in the watchlist
                except IntegrityError:
                    pass

            elif request.POST["watchlist"] == "remove_watchlist":
                
                # Query for data instance then delete it, exception it already deleted or doesn't exist
                try:
                    remove_watchlist = watchlist.objects.get(item=id, user=request.user.id)
                    remove_watchlist.delete()
                except watchlist.DoesNotExist:
                    pass
        
        # Check if user submit their bid value
        elif "bid" in request.POST:

            # Validate bid value that user input
            try:
                bid_value = float(request.POST["bid"])
            except ValueError:
                listing.error = "Invalid Bid"
                bid_value = None

            # Verifing the bid with starting bid
            if bid_value:
                if bid_value < listing.starting_bid:
                    listing.error = "You Cannot Bid Less Than The Starting Bid"
                else:
                    listing.error = None                

                # If the listing have other bid than starting bid
                
                if listing.current_bid:
                    if bid_value >= listing.starting_bid and bid_value <= listing.current_bid:
                        listing.error = "Your Bid Must Be Greater Than Current Bid"
                else:
                    listing.error = None

                if not listing.error:
                    
                    # Proceed with the bid
                    user_bid = bid(bid=bid_value, bid_item=listing, bid_user=request.user)
                    user_bid.save()

                    # Update the current bid of item, after user succeeded with the bid 
                    listing.current_bid = bid_value

                    # Update current highest bid, so we'll to find the winner
                    current_bid = bid.objects.filter(bid_item = listing.id).order_by("-bid").first()
                    
        elif "comment" in request.POST:
            
            # If comment is valid
            user_commemt = request.POST["comment"]
            if user_commemt:

                # Save new comment to database
                new_comment = comment(comment=user_commemt, item=listing, commenter=request.user)
                new_comment.save()

                # Update listing comment to render for user
                listing.comment = comment.objects.filter(item_id=listing.id) 

        elif "close" in request.POST:
            if listing.is_owner and listing.is_active:

                # Find the winner with the highest bid
                winner = current_bid.bid_user
                listing.winner = winner

                # Make the listing no longer active
                listing.is_active = False
                
                listing.save()

    # Retrive user id from request if they logged in
    user_id = request.user.id
    
    # Check if user have the item in their watchlist
    try:
        watchlist.objects.get(user=user_id, item=id)
        listing.in_watchlist = True
    except watchlist.DoesNotExist:
        listing.in_watchlist = False
    
    return render(request, "auctions/listing.html", {
        "listing": listing
    })

# Display all watchlist for user
@login_required(login_url="login")
def view_watchlist(request):

    # Retrive all watchlists that user have
    watchlists = watchlist.objects.filter(user = request.user)
    
    # Retrive all current bid of the item in watchlists
    for listing in watchlists:
        current_bid = bid.objects.filter(bid_item = listing.item).order_by("-bid").first()
        if current_bid:
            listing.item.current_bid = current_bid.bid
        else:
            listing.item.current_bid = None


    return render(request, "auctions/watchlist.html", {
        "watchlists": watchlists
    })

def category(request):
    
    # Retrive all categories from the table
    categories = Category.objects.all()
    
    # Count number of listing in a category
    # counts = {}
    # for category in categories:
    #     print(category.items.all())

    return render(request, 'auctions/category.html', {
        'categories': categories,
    })

def category_listing(request, id):
    
    # Retrive category
    category = Category.objects.get(id = id)

    # Retrive listing in that category
    listings = item.objects.filter(categories = id)
    
    # Retrive current bid
    for listing in listings:
        current_bid = bid.objects.filter(bid_item = listing.id).order_by("-bid").first()
        if current_bid:
            listing.current_bid = current_bid.bid
        else:
            listing.current_bid = None


    return render(request, "auctions/category_listing.html", {
        "listings": listings,
        "category": category,
    })