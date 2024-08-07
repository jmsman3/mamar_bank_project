from django.db import models
from django.contrib.auth.models import User
from .constant import ACCOUNT_TYPE,GENDER_TYPE
# Create your models here.


class UserBankAccount(models.Model):
    user = models.OneToOneField(User , related_name='account', on_delete=models.CASCADE)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE )
    account_no = models.CharField(unique=True , max_length=10) #account name duijon user er same hobe na
    birth_date = models.DateField(null=True, blank=True) #ke o faka rakhle o somossa nai
    gender = models.CharField(max_length=10, choices=GENDER_TYPE)
    initial_deposite_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2 ) # ekjon user 12 digit obdi taka rakhte parbe and dui dosomik porjonto taka rakhte parbe jemon 1000.50
    is_bankrupt = models.BooleanField(default=False)
    def __str__(self):
        return str(self.account_no)
    
class UserAddress(models.Model):
    user = models.OneToOneField(User , related_name='address', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code =models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user.email)
        
