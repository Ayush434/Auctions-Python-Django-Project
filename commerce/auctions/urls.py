from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("showListing/<int:item_id>", views.showListing, name="showListing"),
    path("addToWatchlist/<int:itemID>", views.addToWatchlist, name="addToWatchlist"),
    path("addComments/<int:item_id>", views.addComments, name="addComments"),
    path("watchList", views.watchList, name="watchList"),
    path("closed", views.closed, name="closed"),
    path("closeListing/<int:clID>", views.closeListing, name="closeListing"),
    path("showCategory/<str:name>", views.showCategory, name="showCategory"),
    path("categories", views.categories, name="categories"),
    
]
