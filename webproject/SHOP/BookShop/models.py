from django.db import models
from django.contrib.auth.models import User

class product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(max_length=500) 
    stock = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.name} : {self.price}'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class orderedproduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField( default=1)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,   
    )
    
    def cost(self):
        return self.product.price * self.amount
    
    def __str__(self):
        return f"{self.user.username}: {self.amount} of {self.product.name}"
        

        



