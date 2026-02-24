from django.contrib import admin
from .models import User, AuctionListing, Bid, Comment

# Register your models here.
# Registrando os modelos para que apareçam na interface do Admin
admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(Bid)
admin.site.register(Comment)