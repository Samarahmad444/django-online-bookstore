from django.urls import path
from . import views

app_name ="BookShop"
urlpatterns=[
    path("", views.login , name='login'),
    path("registeration", views.registeration , name='registeration'),
    path("products", views.products , name='products'),
    path("logout", views.logout , name='logout'),
    path("product_detail/<int:product_id>/", views.product_detail , name='product_detail'),
    path("add_to_cart/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    path("basket", views.basket, name="basket"),
    path("order", views.order, name="order"),
    path("delete/<int:id>",views.delete,name="delete"),
    path("empty/", views.empty, name="empty")
]
