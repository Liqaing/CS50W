from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from .models import User, item, bid, comment


def index(request):
    return render(request, "auctions/index.html")


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

def create_listing(request):
    if request.method == "POST":

        # Get all data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]

        # Validate data that user submit
        error_dict = {}
        
        if not title:
            error_dict["missing_title"] = "Listing title is missing"
        if not description:
            error_dict["missing_description"] = "Listing description is missing"
        if not starting_bid:
            error_dict["missing_starting_bid"] = "Listing starting bid is missing"

        # Validate url of image_url
        validate_url = URLValidator(verify_exists=True)
        try:
            validate_url(image_url)
        except ValidationError:
            error_dict["invalid_image_url"] = "Invalid Url For Image"


        # Create item object and add its to the item database
        new_item = item(title=title, description=description, starting_bid=starting_bid, image_url=image_url)
        new_item.save()

        # item.add_to_class(title, description, starting_bid, image_url)
        # print(title, description, starting_bid, image_url)

        return HttpResponseRedirect(reverse("index"))
                 
    return render(request, "auctions/create_listing.html")