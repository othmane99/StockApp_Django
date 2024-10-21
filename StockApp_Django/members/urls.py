from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import login_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # Add other paths as needed
]
