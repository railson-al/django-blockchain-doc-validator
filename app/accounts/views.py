from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')  # Redireciona para a página inicial após o registro
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Usando auth_login em vez de login
                messages.success(request, f"Bem-vindo, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Usuário ou senha inválidos.")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    auth_logout(request)
    messages.success(request, "Você foi desconectado com sucesso.")
    return redirect('home')  # Substitua 'home' pelo nome da sua URL da página inicial

def index(request):
    return render(request, 'accounts/home.html', {})