from django.urls import path, include
from energyMeter import views
urlpatterns = [
    path('home', views.homepage),
    path('updateDashboard', views.updateDashboard, name="energy_new"),
]
