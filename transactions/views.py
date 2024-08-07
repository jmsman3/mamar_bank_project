from typing import Any
from django.db.models.query import QuerySet
from django.views.generic import CreateView ,ListView
from .models import Transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import DepositForm,WithdrawForm,LoanRequestForm  ,BalanceTransferForm
from transactions.constants import DEPOSIT,WITHDRAWAL,LOAN,LOAN_PAID,TRASNFER_MONEY
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum
from datetime import datetime
from django.views import View
from django.shortcuts import get_object_or_404 , redirect
from django.urls import reverse_lazy
from django.core.mail import EmailMessage ,EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.

def send_transaction_email(user,amount ,subject ,template):
    message = render_to_string(template ,{'user':user, 'amount' : amount})
    
    send_email = EmailMultiAlternatives( subject, '' , to=[user.email])
    send_email.attach_alternative(message ,'text/html')
    send_email.send()


class TransactionCreateMixin(CreateView ,LoginRequiredMixin):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title =''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs=  super().get_form_kwargs()
        kwargs.update({
            'account' : self.request.user.account,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #template e context data pass kora
        context.update({
            'title' : self.title
        })
        return context

class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title ='Deposit'

    def get_initial(self):
        print('inside deposit')
        initial = {'transaction_type': DEPOSIT }  
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount # account balance = 500 , ami deposit korlam =1000, new balance holo = 1500
        account.save(
            update_fields = ['balance']
        )
        
        messages.success(self.request, f"${amount} was deposited to your account successfully")
        send_transaction_email( self.request.user ,amount ,'Deposite Message' ,'transactions/deposite_email.html')
        return super().form_valid(form)

class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title ='Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type' : WITHDRAWAL }
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f"Successfullt withdrawn {amount}$ from  your account successfully")
        send_transaction_email( self.request.user ,amount ,'Withdrawal Message' ,'transactions/withdrawal_email.html')
        return super().form_valid(form)
        
class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title ='Request For Loan'

    def get_initial(self):
        initial = {'transaction_type' : LOAN }
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(account = self.request.user.account,transaction_type= 3,loan_approve = True).count()

        if current_loan_count >=3:
            return HttpResponse("You have Cross Your Loan Limit")
       
        messages.success(self.request, f"Loan request for {amount}$ has been successfully sent to admin")
        send_transaction_email( self.request.user ,amount ,'Loan Request Message' ,'transactions/loan_email.html')
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0

    def get_queryset(self):
        queryset =  super().get_queryset().filter(
            account = self.request.user.account 
        )       

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            queryset = queryset.filter(timestamp__date__gte = start_date ,timestamp__date__lte = end_date)
            
            self.balance = Transaction.objects.filter( timestamp__date__gte = start_date ,timestamp__date__lte = end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
        return queryset.distinct() #unique query set hote hobe
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #template e context data pass kora
        context.update({
            'account': self.request.user.account
        })
        return context


class PayLoanView(LoginRequiredMixin,View):
    def get(self,request, loan_id):
        loan = get_object_or_404(Transaction ,id = loan_id)

        if loan.loan_approve: #ekjon user loan pay orte parbe tokhon e jokhon tar loan approve hobe
            user_account = loan.account 
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()

                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
        else:
            messages.error(self.request , f"Loan amount is Greater than amount balance")
            return redirect('loan_list')

class LoanListView(LoginRequiredMixin , ListView):
    model = Transaction
    template_name ='transactions/loan_request.html'
    context_object_name = 'loans'

    def get_queryset(self):
        user_account = self.request.user.account
        queryset= Transaction.objects.filter( account = user_account ,transaction_type= LOAN )
        return queryset

class BalanceTransferView(TransactionCreateMixin):
    form_class = BalanceTransferForm
    template_name = 'transactions/balance_transfer.html'
    title = 'Transfer Balance'
    success_url = reverse_lazy('transaction_report')

    def get_initial(self):
        initial = {'transaction_type' : TRASNFER_MONEY }
        return initial
    
    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        recipient_account = form.cleaned_data.get('to_account')
        account = self.request.user.account

        account.balance -= amount
        account.save(update_fields = ['balance'])   #je taka pathabe 

        recipient_account.balance += amount
        recipient_account.save(update_fields=['balance']) # jar kache taka pathabe

        messages.success(self.request, f"{amount}$ has been Transfered to {recipient_account.user.username} successfully")
        return super().form_valid(form)
