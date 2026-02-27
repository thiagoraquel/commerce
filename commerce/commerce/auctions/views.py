from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, AuctionListing
from .forms import ListingForm

def index(request):
# Buscamos apenas as listagens que estão marcadas como ativas
    listings = AuctionListing.objects.filter(is_active=True)
    
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

def create_listing(request):
    # Se o usuário não estiver logado, ele não pode criar anúncios
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        # O usuário preencheu o formulário e clicou em "Salvar"
        form = ListingForm(request.POST)
        if form.is_valid():
            # Criamos o objeto mas não salvamos no banco ainda (commit=False)
            # porque precisamos dizer quem é o dono (owner)
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return redirect("index") # Volta para a página inicial
    else:
        # O usuário apenas entrou na página (GET), enviamos o formulário vazio
        form = ListingForm()

    return render(request, "auctions/create.html", {
        "form": form
    })

def listing_page(request, listing_id):
    # Busca o item pelo ID ou retorna erro 404 se não achar
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    return render(request, "auctions/listing.html", {
        "listing": listing
    })

def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    if request.user in listing.watchlist.all():
        listing.watchlist.remove(request.user)
    else:
        listing.watchlist.add(request.user)
    return redirect("listing_page", listing_id=listing_id)