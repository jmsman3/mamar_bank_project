from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSACTIONS_TYPE
# Create your models here.

class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount,on_delete=models.CASCADE,related_name='transactions') #ekjon user er multiple transactions hote pare 
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction= models.DecimalField(decimal_places=2,max_digits=12)
    transaction_type = models.IntegerField(choices=TRANSACTIONS_TYPE,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False)
   
    
    class Meta:
        ordering = ['timestamp']
        
