from django.urls import path
from . import views

app_name = 'dashboard'
import .views DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]
