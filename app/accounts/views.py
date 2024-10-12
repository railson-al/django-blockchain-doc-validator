from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import hashlib
from .blockchain import register_document, verify_document
from .forms import UserRegistrationForm, DocumentUploadForm
from .models import Document

def index(request):
    return render(request, 'accounts/home.html', {})


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


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            
            # Gerar hash do documento
            file_hash = hashlib.sha256(document.file.read()).hexdigest()
            
            # Registrar na blockchain
            tx_receipt = register_document(file_hash)
            
            # Salvar o hash da transação
            document.blockchain_tx_hash = tx_receipt['transactionHash'].hex()
            document.save()

            messages.success(request, 'Documento enviado com sucesso e registrado na blockchain.')
            return redirect('document_list')
    else:
        form = DocumentUploadForm()
    return render(request, 'app/upload_document.html', {'form': form})


@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user)
    return render(request, 'accounts/document_list.html', {'documents': documents})


def verify_document_view(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('document')
        if uploaded_file:
            # Calcular o hash do documento enviado
            file_hash = hashlib.sha256(uploaded_file.read()).hexdigest()
            
            # Verificar o hash na blockchain
            is_verified = verify_document(file_hash)
            
            return render(request, 'accounts/verify_document.html', {
                'is_verified': is_verified,
                'file_hash': file_hash
            })
    
    return render(request, 'app/verify_document.html')