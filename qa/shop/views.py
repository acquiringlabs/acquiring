from django.shortcuts import render


def shop(request):
    context = {}
    return render(request, "shop/shop.html", context)


def cart(request):
    context = {}
    return render(request, "shop/cart.html", context)


def checkout(request):
    context = {}
    return render(request, "shop/checkout.html", context)
