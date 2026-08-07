from datetime import timedelta

from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import restaurant_task
from celery.result import AsyncResult

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


@csrf_exempt
def scrape_restaurant(request):
    # user = request.user
    # if not user.is_authenticated:
    #     return JsonResponse({'detail': 'User not authenticated'}, status=401)

    restaurant_url = request.POST.get('url')
    # time_for_reservation = request.POST.get('reservationFor')
    time_for_reservation = "20:00:00 08/08/2025"  # Placeholder for testing
    next_hour = timezone.now()#.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)      
    result = restaurant_task.apply_async(
        args=[restaurant_url, time_for_reservation],
        eta=next_hour,
    )
    return JsonResponse({'detail': 'Scraping task started', 'task_id': result.id}, status=202)

@csrf_exempt
def get_task_status(request, task_id):
    try:
        result = AsyncResult(task_id)
        if result.ready():
            return JsonResponse({'status': 'SUCCESS', 'result': result.result}, status=200)
        else:
            return JsonResponse({'status': 'PENDING'}, status=200)
    except Exception:
        return JsonResponse({'status': 'unknown'}, status=404)