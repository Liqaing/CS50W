from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.create_listing, name="create-listing"),
    path("listings/<str:id>", views.view_listing, name="view-listing"),
    path("watchlist", views.view_watchlist, name="watchlist"),
    path("category", views.category, name="category"),
    path("category/<str:id>", views.category_listing, name="category_listing"),
]
