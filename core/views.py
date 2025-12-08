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
            messages.success(request, f'Vous avez créé un compte avec succès {user.username}!')
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
                messages.success(request, f'Bienvenue, {username}!')
                return redirect('floor_plan')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe invalide.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


@login_required
def floor_plan(request):
    today = timezone.now().date()
    
    # Get the current month's start and end
    import calendar
    _, last_day = calendar.monthrange(today.year, today.month)
    start_of_month = today.replace(day=1)
    end_of_month = today.replace(day=last_day)
    
    # Generate list of Mon-Fri days in the month
    month_days = []
    
    currentUserBookings = Booking.objects.filter(
        user=request.user, 
        date__range=[start_of_month, end_of_month]
    ).values_list('date', flat=True)

    added_first_day = False
    
    for i in range(last_day):
        day = start_of_month + timedelta(days=i)
        
        # Skip Saturday (5) and Sunday (6)
        if day.weekday() >= 5:
            continue
            
        # Add padding for the first week to align dates with Mon-Fri columns
        if not added_first_day:
            for _ in range(day.weekday()):
                month_days.append(None)
            added_first_day = True
            
        month_days.append({
            'date': day,
            'day_name': day.strftime('%A'),
            'is_today': day == today,
            'has_booking': day in currentUserBookings
        })

    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    # Validate selected date is within the displayed month
    if selected_date.month != today.month or selected_date.year != today.year:
        selected_date = today
        
    # If selected date is a weekend, default to today (or nearest weekday if today is weekend)
    if selected_date.weekday() >= 5:
        selected_date = today
        # If today is also weekend, find next Monday
        if selected_date.weekday() >= 5:
             days_ahead = 7 - selected_date.weekday() # 0=Mon
             selected_date = selected_date + timedelta(days=days_ahead)
             # Check if we jumped to next month
             if selected_date.month != today.month:
                 selected_date = today.replace(day=1) 
                 while selected_date.weekday() >= 5:
                     selected_date += timedelta(days=1)

    desks = Desk.objects.all()
    bookings = Booking.objects.filter(date=selected_date)
    
    # Create a map of desk_id to booking object (to access user)
    desk_booking_map = {booking.desk_id: booking for booking in bookings}
    
    my_booking = bookings.filter(user=request.user).first()
    
    desk_data = []
    for desk in desks:
        status = 'available'
        booked_by_name = None

        if desk.id in desk_booking_map:
             status = 'booked'
             booked_by_name = desk_booking_map[desk.id].user.username

        if my_booking and my_booking.desk.id == desk.id:
            status = 'my_booking'
            
        desk_data.append({
            'desk': desk,
            'status': status,
            'booked_by': booked_by_name
        })

    context = {
        'desk_data': desk_data,
        'selected_date': selected_date,
        'my_booking': my_booking,
        'month_days': month_days, 
    }
    return render(request, 'core/floor_plan.html', context)

@login_required
def book_desk(request, desk_id):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Date invalide.")
            return redirect('floor_plan')

        # Validate date is within current month (or reasonable range)
        today = timezone.now().date()
        import calendar
        _, last_day = calendar.monthrange(today.year, today.month)
        start_of_month = today.replace(day=1)
        end_of_month = today.replace(day=last_day)
        
        if date < start_of_month or date > end_of_month:
             messages.error(request, "Vous pouvez seulement réserver des bureaux pour le mois en cours.")
             return redirect('floor_plan')
             
        if date.weekday() >= 5:
            messages.error(request, "Les réservations sont fermées le week-end.")
            return redirect(f'/floor_plan/?date={date_str}')

        # Check if user already has a booking for this date
        if Booking.objects.filter(user=request.user, date=date).exists():
            messages.error(request, "Vous avez déjà une réservation pour cette date.")
            return redirect(f'/floor_plan/?date={date_str}')

        # Check if desk is already booked
        if Booking.objects.filter(desk_id=desk_id, date=date).exists():
            messages.error(request, "Ce bureau est déjà réservé.")
            return redirect(f'/floor_plan/?date={date_str}')

        desk = get_object_or_404(Desk, id=desk_id)
        Booking.objects.create(user=request.user, desk=desk, date=date)
        messages.success(request, f"Vous avez réservé avec succès {desk.name}.")
        return redirect(f'/floor_plan/?date={date_str}')
    
    return redirect('floor_plan')

@login_required
def unbook_desk(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        date_str = booking.date.strftime('%Y-%m-%d')
        booking.delete()
        messages.success(request, "Votre réservation a été annulée.")
        return redirect(f'/floor_plan/?date={date_str}')
    
    return redirect('floor_plan')
