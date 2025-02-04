from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),      
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create', views.create, name='create'),
    path('categories', views.categories, name='categories'),      #leads to the categories
    path('category/<str:value>', views.category, name='category'),  # one category 
    path('view/<int:listing_id>', views.view_listing, name='view'),     # leads to the view of a single listing 
    path('add/<int:listing_id>', views.watchlist_add, name='add'),
    path('delete/<int:listing_id>', views.watchlist_delete, name='delete'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('bid/<int:listing_id>', views.bid, name='bid'),
    path('close/<int:listing_id>', views.close, name='close'),
    path('comment/<int:listing_id>', views.comment, name='comment')
]
