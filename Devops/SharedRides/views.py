from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import Trip
from .forms import RegisterUserForm
from .forms import TripForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

def dashboard(request):
    if request.user.is_authenticated:
        upcoming_trips = Trip.objects.filter(departure_time__gt=timezone.now())

        context = {
            'num_upcoming_trips': upcoming_trips.count(),
        }
        return render(request, 'index.html', context)
    else:
        return redirect('login')

def registeration(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterUserForm()
    return render(request, 'register_user.html', {'form': form})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'registr_user.html')

def trip_details(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    return render(request, 'trip_details.html', {'trip': trip})

def trip_list(request):
    query = request.GET.get('q')
    trips = Trip.objects.all()

    if query:
        trips = trips.filter(
            Q(departure_location__icontains=query) |
            Q(destination__icontains=query) |
            Q(driver__username__icontains=query)
        )

    return render(request, 'trip_list.html', {'trips': trips, 'query': query})

def create_trip(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('trip_list')
    else:
        form = TripForm()

    return render(request, 'create_trip.html', {'form': form})

def update_trip(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    
    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.driver = request.user  
            trip.save()
            return redirect('trip_details', trip_id=trip_id)
    else:
        form = TripForm()
    
    return render(request, 'update_trip.html', {'form': form, 'trip': trip})

def delete_trip(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    
    if request.method == 'POST':
        trip.delete()
        return redirect('trip_list')
    
    return render(request, 'delete_trip.html', {'trip': trip})