from django.shortcuts import render ,redirect
from .forms import UserRegistrationForm ,UserUpdateForm
from django.contrib.auth import login,logout
from django.views.generic import FormView ,UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView,LogoutView 
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
        
