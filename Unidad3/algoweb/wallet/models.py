from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=58)  
    private_key = models.TextField() 

    def __str__(self):
        return f"Wallet de {self.user.username}"
    
class SmartContract(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    teal_file = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    txid = models.CharField(max_length=100, null=True, blank=True)
    app_id = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
