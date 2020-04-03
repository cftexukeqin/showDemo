from django.urls import path
from . import views

urlpatterns = [
    path('bar/', views.ChartView.as_view(), name='bar'),
    path('line/', views.LineView.as_view(), name='line'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('upload/', views.upload_csv, name='upload'),
    path('img/', views.bar_img, name='bar'),
    path('del/', views.delete_data, name='del'),
]