from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signup(request):
    form = request.POST
    username = form.get('username', "")
    password = form.get('password', "")
    email = form.get('email', "")
    if not username or not password or not email:
        return JsonResponse({'detail': 'Missing required fields'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'detail': 'Username already exists'}, status=400)
    
    user = User.objects.create_user(username=username, password=password, email=email)
    user.save()
    login(request, user)
    return JsonResponse({'detail': 'User created successfully'}, status=201)

@csrf_exempt
def signin(request):
    form = request.POST
    username = form.get('username', "")
    password = form.get('password', "")
    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)
    
    login(request, user)
    return JsonResponse({'detail': 'Signed in successfully'}, status=200)



def scrape_restaurant(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'detail': 'User not authenticated'}, status=401)

    restaurant_url = request.POST.get('url')
