from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Transaction , UserBankAccount

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount' ,'transaction_type']
    
    
    def __init__(self, *args , **kwargs):
        self.user_account = kwargs.pop('account') #account value k pop kore anlam
        super().__init__(*args , **kwargs)
        self.fields['transaction_type'].disabled = True #ai filed disabled thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe 


    def save(self, commit= True):
        self.instance.account = self.user_account
        self.instance.balance_after_transaction = self.instance.account.balance 
        return super().save()
    
class DepositForm(TransactionForm):
    def clean_amount(self): #amount field k filter korlam
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount') #User er fill up kora form theke amra amount field er value k neye aslam
        if amount < min_deposit_amount:
            raise forms.ValidationError(f'You need to deposit at least {min_deposit_amount} $')      
        return amount
    
class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.user_account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance   #1000
        amount = self.cleaned_data.get('amount') 


        if account.is_bankrupt:
            raise forms.ValidationError("The Bank is now bankrupt, no transactions will be processed.")
        
        if amount < min_withdraw_amount:
            raise forms.ValidationError(f'You can withdraw at least {min_withdraw_amount} $')
        if amount > max_withdraw_amount:
            raise forms.ValidationError(f'You can withdraw at most {max_withdraw_amount} $')
        if amount > balance:
            raise forms.ValidationError(f'You have {balance} $ in your account.' 'You can not withdraw more than your account balance')       
        return amount
 







class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        return amount
    
class BalanceTransferForm(TransactionForm):
    to_account = forms.IntegerField() #jare taka pathabo tar field ,aita models.py te kora jabe na ai khane e kora valo 
    
    class Meta:
        model = Transaction
        fields = ['amount','to_account' , 'transaction_type']


    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        account = self.user_account
        balance = account.balance 
        min_transaction_amount = 20
        max_transaction_amount= 10000
        
        if amount < min_transaction_amount:
            raise forms.ValidationError(f"Your Transfer amount must be at least ${min_transaction_amount}")
        if amount > max_transaction_amount:
            raise forms.ValidationError(f'Your Transfer amount must be at Most ${max_transaction_amount}')
        if amount > balance:
            raise forms.ValidationError(f"You dot have Sufficoent balance. Your balance is ${balance}")
        return amount
        
    def clean_to_account(self):
        to_account = self.cleaned_data.get('to_account')
       
        try:
            recipient_account = UserBankAccount.objects.get( account_no = to_account)
        except UserBankAccount.DoesNotExist:
            raise forms.ValidationError('Wrong account number,Receipent account Does not exist')
        return recipient_account

    def save(self, commit = True):
        self.instance.account = self.user_account
        self.instance.balance_after_transaction = self.user_account.balance-self.cleaned_data['amount']
        return super().save()





