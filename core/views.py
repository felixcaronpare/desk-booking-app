from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.contrib import messages
from .models import Desk, Booking
from .forms import UserRegistrationForm
from datetime import datetime, timedelta


def register_view(request):
    if request.user.is_authenticated:
        return redirect('floor_plan')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('floor_plan')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('floor_plan')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('floor_plan')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def floor_plan(request):
    today = timezone.now().date()
    # Calculate start of the week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    
    # Generate list of 5 workdays (Mon-Fri)
    week_days = []
    for i in range(5):
        day = start_of_week + timedelta(days=i)
        week_days.append({
            'date': day,
            'day_name': day.strftime('%A'),
            'is_today': day == today
        })

    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    # Ensure selected date is within the current work week (Mon-Fri)
    # If not, default to Monday of current week (or today if it's a workday)
    if selected_date < start_of_week or selected_date > start_of_week + timedelta(days=4):
         if today >= start_of_week and today <= start_of_week + timedelta(days=4):
             selected_date = today
         else:
             selected_date = start_of_week

    desks = Desk.objects.all()
    bookings = Booking.objects.filter(date=selected_date)
    
    booked_desk_ids = bookings.values_list('desk_id', flat=True)
    my_booking = bookings.filter(user=request.user).first()
    
    desk_data = []
    for desk in desks:
        status = 'available'
        if desk.id in booked_desk_ids:
            status = 'booked'
        if my_booking and my_booking.desk.id == desk.id:
            status = 'my_booking'
            
        desk_data.append({
            'desk': desk,
            'status': status
        })

    context = {
        'desk_data': desk_data,
        'selected_date': selected_date,
        'my_booking': my_booking,
        'week_days': week_days,
    }
    return render(request, 'core/floor_plan.html', context)

@login_required
def book_desk(request, desk_id):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date.")
            return redirect('floor_plan')

        # Validate date is within current work week
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4)
        
        if date < start_of_week or date > end_of_week:
             messages.error(request, "You can only book desks for the current work week (Mon-Fri).")
             return redirect('floor_plan')

        # Check if user already has a booking for this date
        if Booking.objects.filter(user=request.user, date=date).exists():
            messages.error(request, "You already have a booking for this date.")
            return redirect(f'/floor_plan/?date={date_str}')

        # Check if desk is already booked
        if Booking.objects.filter(desk_id=desk_id, date=date).exists():
            messages.error(request, "This desk is already booked.")
            return redirect(f'/floor_plan/?date={date_str}')

        desk = get_object_or_404(Desk, id=desk_id)
        Booking.objects.create(user=request.user, desk=desk, date=date)
        messages.success(request, f"You have successfully booked {desk.name}.")
        return redirect(f'/floor_plan/?date={date_str}')
    
    return redirect('floor_plan')

@login_required
def unbook_desk(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        date_str = booking.date.strftime('%Y-%m-%d')
        booking.delete()
        messages.success(request, "Booking cancelled.")
        return redirect(f'/floor_plan/?date={date_str}')
    
    return redirect('floor_plan')
