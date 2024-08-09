from django.shortcuts import render ,redirect
from .forms import UserRegistrationForm ,UserUpdateForm
from django.contrib.auth import login,logout
from django.views.generic import FormView ,UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView,LogoutView 
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.mail import EmailMessage ,EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.

class UserRegistrationView(FormView):
    template_name ='accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        # print(form.cleaned_data)
        user = form.save()
        login(self.request,user)
        # print(user)
        return super().form_valid(form) #form valid function call hobe jodi sob thik thake

class UserLoginView(LoginView):
    template_name ='accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')

class UserLogoutview(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')

class UserBankAccountUpdateView(UpdateView):
    template_name = 'accounts/profile.html'

    def get(self,request):  #context aakar e pathano holo
        form = UserUpdateForm(instance=request.user)
        return render(request , self.template_name ,{'form': form})
    
    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request , self.template_name , {'form':form})

def send_transaction_email(user  ,subject ,template):
    message = render_to_string(template ,{'user':user, })
    
    send_email = EmailMultiAlternatives( subject, '' , to=[user.email])
    send_email.attach_alternative(message ,'text/html')
    send_email.send()


def pass_change2(request):
    # return HttpResponse('hello world')
    if  request.user.is_authenticated:
        if request.method =='POST':
            form = SetPasswordForm(user=request.user ,data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request , form.user)
                send_transaction_email(request.user ,'Password Update confirmation' ,'accounts/pass_change_email.html')
                messages.success(request, f"{request.user.first_name} {request.user.last_name} Your Password Updated successfully")

                return redirect('profile')
        else:
            form = SetPasswordForm(user= request.user)
        return render(request , 'accounts/passchange.html' , {'form' : form})
    else:
        return redirect('login')