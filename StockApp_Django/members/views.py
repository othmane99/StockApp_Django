from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Check user permissions and redirect accordingly
            if user.has_perm('your_app.some_permission'):
                return redirect('some_view')  # Replace 'some_view' with the appropriate view name
            else:
                return redirect('home')  # Default redirection
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'authentication/login.html')  # Use the correct path to your custom template

@login_required
def home_view(request):
    # Home view logic
    return render(request, 'home.html')
