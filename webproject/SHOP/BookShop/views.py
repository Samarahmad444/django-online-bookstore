from django.shortcuts import render 
from .models import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect  
from django.urls import reverse
from django.contrib import messages 


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect(reverse("BookShop:products"))
        else:
            return render(request, "BookShop/login.html", {
                "message": "Invalid username or password."
            })
    
    return render(request, "BookShop/login.html")


def registeration(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        
    
        if not username or not password or not email:
            return render(request, "BookShop/registeration.html", {
                "message": "Please fill in all fields."
            })
        
        
        if User.objects.filter(username=username).exists():
            return render(request, "BookShop/registeration.html", {
                 "message": "Username already exists."
            })
        user = User.objects.create_user(username=username,
        email=email,
        password=password)
        user.save()
        messages.success(request, "Your account has been created successfully! You can now log in")
        return HttpResponseRedirect(reverse("BookShop:login"))
    
    return render(request, "BookShop/registeration.html")

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("BookShop:login")) 


def products(request):    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("BookShop:login"))
    
    prod = product.objects.all()
    return render(request, "BookShop/products.html", {
        "products": prod
    })

def product_detail(request, product_id):    
    productt = product.objects.get(id=product_id)
    return render(request, "BookShop/product_detail.html", {
        "product": productt
    })

def add_to_cart(request, product_id):
    productt = product.objects.get(id=product_id)   
    user = request.user                             

    if request.method == "POST":
        amount = int(request.POST["amount"])
       
        if productt.stock <= 0:#when the user try to add out of stock product to the basket, it will redirect the user to the basket page and display a message.
            return render(request, "BookShop/basket.html", {
                 "message": f"Book:'{productt.name}' is out of stock."})
        
        if amount > productt.stock:#when the user try to add amount of product more than the avalible stock, it will redirect the user to the basket page and display a message.
             return render(request, "BookShop/basket.html", {
                 "message": f"Only {productt.stock} items of '{productt.name}' are available."})

        existProduct = orderedproduct.objects.filter(
            user=user,
            product=productt,
            order__isnull=True
        ).first()

        if existProduct:
            if existProduct.amount + amount>existProduct.product.stock:# if the user try to add the same product again, it will check if new amount of the product + the amount of the same product in the user basket will eexcess the stock
                messages.warning(request,
                    f"You already have {existProduct.amount} " 
                    f"of '{existProduct.product.name}' in your basket. "
                    f"Only you can add {existProduct.product.stock-existProduct.amount} of this book."
                )# if the condition is true, it will redirect the user to products page and show message
                return HttpResponseRedirect(reverse("BookShop:products"))
            else:
                existProduct.amount += amount
                existProduct.save()
        else:
            order = orderedproduct(user=user, product=productt, amount=amount)
            order.save()
    return HttpResponseRedirect(reverse("BookShop:products"))

def basket(request):
    user = request.user
    message = None
    removed = orderedproduct.objects.filter(#return out of srtock products in the user basket.
        user=user,
        order__isnull=True,          
        product__stock__lte=0        
    )

    if removed.exists():#check if there are of srtock products in the user basket.
        rnames = []#list of names of out of stock products in the user basket.(empty in the beginning)

        for r in removed:
          rnames.append(r.product.name)#adds name of out of stock products in the user basket to the list.
        removed.delete()#remove out of stock products from the user basket.
        message= "We removed these products from your basket because they are out of stock: "+ ", ".join(rnames)
           
        
    if request.method == "POST":
        product_id = request.POST.get("item_id")
        new_amount = request.POST.get("amount")

        if product_id and new_amount:
            productt = orderedproduct.objects.get(id=product_id, user=user, order__isnull=True)
            new_amount = int(new_amount)
            pStock= productt.product.stock
            if new_amount > pStock:#when the user try to update the amount of the product from the basket, it will check if the amount more than the stock
                message= f"Only {pStock} items of '{productt.product.name}' are available."#when the condition is true, it wiil show a message and keep the old amount
            else:   
                productt.amount = new_amount
                productt.save()
                return HttpResponseRedirect(reverse("BookShop:basket"))
    
    products = orderedproduct.objects.filter(user=user,order__isnull=True)
   
    total = 0
    for p in products:
        total += p.product.price * p.amount

    return render(request, "BookShop/basket.html", {
        "products": products,
        "total": total,
        "message": message
    })
    
def delete(request, id):
    product = orderedproduct.objects.get(id=id)
    product.delete()
    return HttpResponseRedirect(reverse("BookShop:basket"))

def empty(request):
 orderedproduct.objects.filter(user=request.user).delete()
 return  HttpResponseRedirect(reverse("BookShop:basket"))

def order(request):
    user = request.user
    products = orderedproduct.objects.filter(user=user,order__isnull=True)
    total=0
    for p in products:
        total+=p.product.price*p.amount

    if request.method == "POST":
        if not products.exists():
            return render(request, "BookShop/basket.html", {
                 "message": "You cannot place an order, because Your basket is empty."})

        for p in products:
            if p.product.stock <= 0:#when the user try to add out of stock product to the basket, it will redirect the user to the basket page and display a message.
               return render(request, "BookShop/basket.html", {
                 "message": f"Book:'{p.product.name}' is out of stock."})
                

            if p.amount > p.product.stock:#when the user try to add amount of product more than the avalible stock, it will redirect the user to the basket page and display a message.
                return render(request, "BookShop/basket.html", {
                 "message": f"Only {p.product.stock} items of '{p.product.name}' are available."})
        
        order = Order.objects.create(user=user, total=total)


        for p in products:
            p.order = order
            p.save()
            p.product.stock -= p.amount #decrease the stock of the product
            p.product.save()# save the updated product

        messages.success(request, "Your order has been placed successfully!")
        
        return  HttpResponseRedirect(reverse("BookShop:basket"))

    return render(request, "BookShop/order.html", {
        "products": products,
        "total": total
    })






    
