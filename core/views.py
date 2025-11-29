from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Desk, Booking
from datetime import datetime

@login_required
def floor_plan(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    desks = Desk.objects.all().order_by('row', 'col')
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
