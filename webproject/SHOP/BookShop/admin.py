from django.contrib import admin
from .models import product , orderedproduct, Order

admin.site.register(product)
admin.site.register(orderedproduct)
admin.site.register(Order)
# Register your models here.
