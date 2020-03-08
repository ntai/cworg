from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.redirect_to_current_user, name='index'),
    path('<int:pk>/', views.UserProfileView.as_view(), name='user_detail'),
    path('api/', include('userprofile.api.urls')),
]
