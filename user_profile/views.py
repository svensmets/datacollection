from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView, View
from user_profile.forms import LoginForm


class LoginPage(FormView):
    """
    Logs a user into the application if username and password is correct
    """
    def get(self, request):
        """Show login page"""
        form = LoginForm()
        return render(request, 'user_profile/login.html', {'form': form})

    def post(self, request):
        """
        Login user if valid password and username is submitted
        """
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                login(request, user)
                return HttpResponseRedirect('/overview/')
            else:
                message = 'user not found'
                return render(request, 'user_profile/login.html', {'login_message': message, 'form': form})
        else:
            message = 'Please fill in valid fields'
            return render(request, 'user_profile/login.html', {'login_message': message, 'form': form})


class LogoutPage(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('/overview/')





