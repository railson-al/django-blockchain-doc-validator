from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from web3 import Web3
import hashlib
from .blockchain import register_document, verify_document
from .forms import UserRegistrationForm, DocumentUploadForm
from .models import Document

def index(request):
    """Renderiza a página inicial."""
    return render(request, 'accounts/home.html', {})


def register(request):
    """Registra um novo usuário."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """Autentica e loga um usuário."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
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
    """Desconecta o usuário."""
    auth_logout(request)
    messages.success(request, "Você foi desconectado com sucesso.")
    return redirect('home')


@login_required
def upload_document(request):
    """Faz o upload de um documento e registra na blockchain."""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()

            # Gerar hash do documento
            document.file.seek(0)  # Certifique-se de que o arquivo é lido desde o início
            file_content = document.file.read()
            file_hash = Web3.keccak(file_content).hex()
            # print(f"Hash do arquivo: {file_hash}")

            try:
                # Registrar na blockchain
                tx_receipt = register_document(file_hash)
                
                # Salvar o hash da transação
                document.blockchain_tx_hash = tx_receipt['transactionHash'].hex()
                document.save()

                messages.success(request, 'Documento enviado com sucesso e registrado na blockchain.')
            except Exception as e:
                messages.error(request, f"Erro ao registrar documento na blockchain: {e}")
            
            return redirect('document_list')
    else:
        form = DocumentUploadForm()
    return render(request, 'accounts/upload_document.html', {'form': form})


@login_required
def document_list(request):
    """Lista os documentos do usuário."""
    documents = Document.objects.filter(user=request.user)
    return render(request, 'accounts/document_list.html', {'documents': documents})


def verify_document_view(request):
    """Verifica se um documento está registrado na blockchain."""
    if request.method == 'POST':
        uploaded_file = request.FILES.get('document')
        if uploaded_file:
            uploaded_file.seek(0)  # Certifique-se de que o arquivo é lido desde o início
            file_hash = hashlib.sha256(uploaded_file.read()).hexdigest()

            try:
                is_verified = verify_document(file_hash)
                messages.success(request, 'Documento verificado com sucesso.' if is_verified else 'Documento não encontrado na blockchain.')
            except Exception as e:
                messages.error(request, f"Erro ao verificar documento na blockchain: {e}")

            return render(request, 'accounts/verify_document.html', {
                'is_verified': is_verified,
                'file_hash': file_hash
            })
    
    return render(request, 'accounts/verify_document.html')
