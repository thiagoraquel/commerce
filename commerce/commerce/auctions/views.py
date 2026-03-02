from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Max
from django.db.models.functions import Coalesce

from .models import User, AuctionListing, Bid
from .forms import ListingForm

def index(request):
# Buscamos as listagens e "anotamos" o valor do maior lance.
    # Se o maior lance for nulo (None), o Coalesce usa o 'starting_bid'.
    listings = AuctionListing.objects.filter(is_active=True).annotate(
        current_price=Coalesce(Max('bids__amount'), 'starting_bid')
    )
    
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
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    # Busca o maior lance atual
    current_bid = listing.bids.order_by('-amount').first()
    
    # Define o preço atual
    current_price = current_bid.amount if current_bid else listing.starting_bid
    
    # Descobre quem é o vencedor (o usuário do maior lance)
    winner = current_bid.user if current_bid else None

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_price": current_price,
        "winner": winner  # Passamos o objeto do usuário vencedor
    })

def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    if request.user in listing.watchlist.all():
        listing.watchlist.remove(request.user)
    else:
        listing.watchlist.add(request.user)
    return redirect("listing_page", listing_id=listing_id)

def watchlist(request):
    # Se não estiver logado, redireciona para login
    if not request.user.is_authenticated:
        return redirect("login")
    
    # Filtra as listagens onde o usuário atual está presente no campo watchlist
    user_watchlist = request.user.watchlist_items.all()
    
    return render(request, "auctions/watchlist.html", {
        "listings": user_watchlist
    })

def place_bid(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=listing_id)
        bid_amount = float(request.POST["bid_amount"])
        
        # Lógica de validação:
        # 1. Buscar o maior lance atual (se houver)
        current_bid = listing.bids.order_by('-amount').first()
        min_required = current_bid.amount if current_bid else listing.starting_bid

        if bid_amount > min_required:
            # Salva o novo lance
            new_bid = Bid(amount=bid_amount, user=request.user, listing=listing)
            new_bid.save()
            return redirect("listing_page", listing_id=listing_id)
        else:
            # Se o lance for baixo demais, você pode passar uma mensagem de erro
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "error": "Bid must be higher than current price.",
                "current_price": min_required

            })
        
def close_auction(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    # Segurança: Apenas o dono pode fechar
    if listing.owner == request.user:
        listing.is_active = False
        listing.save()
        return redirect("listing_page", listing_id=listing_id)
    else:
        return redirect("index")