from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from community.models import Post

User = get_user_model()

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('community:asset_list')
    else:
        form = CustomUserCreationForm()
    context = {'form': form}
    return render(request, 'accounts/signup.html', context)

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('community:asset_list')
    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'accounts/login.html', context)

def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        return redirect('community:asset_list')
    # fallback for GET, though POST is better
    auth_logout(request)
    return redirect('community:asset_list')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'accounts/password_done.html')
    else:
        form = PasswordChangeForm(request.user)
    context = {'form': form}
    return render(request, 'accounts/password_change.html', context)

def profile(request, username):
    person = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=username).order_by('-created_at')
    
    interest_stocks = [s.strip() for s in person.interest_stocks.split(',')] if person.interest_stocks else []
    
    context = {
        'person': person,
        'posts': posts,
        'interest_stocks': interest_stocks,
    }
    return render(request, 'accounts/profile.html', context)
