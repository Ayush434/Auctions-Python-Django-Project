from django.contrib import admin
from .models import Auction, Bids, Comments, User, WatchList, Winner

# Register your models here.


admin.site.register(Auction),
admin.site.register(Bids),
admin.site.register(User),
admin.site.register(WatchList),
admin.site.register(Winner),
admin.site.register(Comments)



