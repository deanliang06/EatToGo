from django.urls import path
from django.http import JsonResponse
from . import views

urlpatterns = [
    path('health', lambda request: JsonResponse({'status': 'ok'})),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('scrape', views.scrape_restaurant, name='scrape_restaurant'),
]