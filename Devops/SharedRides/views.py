from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from .utils import clusterize_latlngs, search
from django.shortcuts import render, redirect
from .models import CustomUser, Request, Trip
import datetime
import json
from operator import attrgetter
from .forms import RegisterUserForm
from .forms import TripForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

def dashboard(request):
    if request.user.is_authenticated:
        upcoming_trips = Trip.objects.filter(time=timezone.now())

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

@login_required
def send_request(request):
    if request.is_ajax() and request.method == 'POST':
        try:
            res = json.loads(request.body)
            trip = Trip.objects.get(pk=res['id'])
            start_place = res['start_place']
            end_place = res['end_place']
            status = 'P'
            cords = res['cords']
            start_lat, start_lng, end_lat, end_lng = cords[0], cords[1], cords[2], cords[3]

            Request.objects.create(from_user=request.user, trip=trip, status=status, start_place=start_place,
                                   start_lat=start_lat, start_lng=start_lng,
                                   end_place=end_place, end_lat=end_lat, end_lng=end_lng)
            return HttpResponse()
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed(['POST'])
    
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def search_trip(request):
    return render(request, 'searchjourney.html')

@login_required
def get_results(request):
    if request.is_ajax() and request.method == "POST":
        try:
            res = json.loads(request.body)
            cords = res['cords']
            cords = cords[0:1] + cords[-1:]
            cords = [[x['d'], x['e']] for x in cords]
            temp = []
            temp.append(cords[0][0])
            temp.append(cords[0][1])
            temp.append(cords[1][0])
            temp.append(cords[1][1])
            distance = res['distance']
            start_place = res['start']
            end_place = res['end']
            radius = int(res['radius'])
            time = datetime.datetime.strptime(res['time'], "%m/%d/%Y %H:%M")
            matched_trips = search(cords, time, radius)

            results = []
            for trip in matched_trips:
                res = {}
                res['id'] = trip.id
                res['startPlace'] = trip.start_place
                res['endPlace'] = trip.end_place
                res['startTime'] = datetime.datetime.strftime(trip.time, "%d %b, %H:%M")
                results.append(res)
            data = json.dumps({'cords': temp, 'start_place': start_place, 'end_place': end_place})
            request.session['data'] = data
            request.session['results'] = results

            return HttpResponse()
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def search_results(request):
    results = request.session.get('results', {})
    '''data = request.session.get('data', {})'''
    data = json.dumps({'key': 'value'})
    return render(request, 'searchResults.html', {'data': data, 'results': results})

@login_required
def request_success(request):
    return render(request, 'requestsuccess.html')

@login_required
def trip_success(request):
    return render(request, 'tripsuccess.html')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def send_request(request):
    if is_ajax(request=request) and request.method == 'POST':
        try:
            res = json.loads(request.body)
            trip = Trip.objects.get(pk=res['id'])
            start_place = res['start_place']
            end_place = res['end_place']
            status = 'P'
            cords = res['cords']
            start_lat = cords[0]
            start_lng = cords[1]
            end_lat = cords[2]
            end_lng = cords[3]

            Request.objects.create(from_user=request.user, trip=trip, status=status, start_place=start_place,
                                   start_lat=start_lat, start_lng=start_lng,
                                   end_place=end_place, end_lat=end_lat, end_lng=end_lng)
            return HttpResponse()
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed(['POST'])

'''@login_required
def sent_requests(request):
    if request.method == 'GET':
        current_sent = request.user.current_sent_requests()
        curr = current_sent.values('id', 'status', 'trip__user__first_name', 'trip__user__last_name',
                                    'start_place', 'end_place', 'trip__time')
        old_sent = request.user.previous_sent_requests()
        old = old_sent.values('id', 'status', 'trip__user__first_name', 'trip__user__last_name',
                               'start_place', 'end_place', 'trip__time')

        return render(request, 'sentrequests.html', {'current': curr, 'expired': old})
    else:
        return HttpResponseNotAllowed(['GET'])
'''
@login_required
def received_requests(request):
    if request.method == 'GET':
        current_received = request.user.current_received_requests()
        curr = current_received.values('id', 'status', 'trip__user__first_name', 'trip__user__last_name', 'start_place', 'end_place', 'trip__time')
        return render(request,'recievedrequest.html',{'current':curr})
    else:
        return HttpResponseNotAllowed(['GET'])

@login_required
def save_journey(request):
    if request.is_ajax() and request.method == "POST":
        try:
            res = json.loads(request.body)
            cords = res['cords']
            cords = [[x['d'], x['e']] for x in cords]
            distance = res['distance']
            start_place = res['start']
            end_place = res['end']
            clusters = clusterize_latlngs(cords, distance)
            time = datetime.datetime.strptime(res['time'], "%m/%d/%Y %H:%M")
            Trip.objects.create(user=request.user, time=time, cluster=json.dumps(clusters), travel_distance=distance,
                                start_place=start_place, end_place=end_place)

            return HttpResponse()
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed(['POST'])