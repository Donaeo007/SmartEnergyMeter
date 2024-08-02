from django.urls import path, include
from energyMeter import views
urlpatterns = [
    path('home', views.homepage),
    path('home2', views.coronahome),
    path('updateDashboard', views.updateDashboard, name="energy_new"),
    path('updateparameters/', views.update_parameters, name='update_parameters'),
    path('download_csv', views.download_csv, name='data download'),
    path('LoadLineChart', views.LoadLineChart),
]
