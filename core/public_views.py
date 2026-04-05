import calendar
from datetime import datetime
from django.shortcuts import render, redirect
from learning.models import TrainingEvent
from .forms import ServiceInquiryForm


def public_index(request):
    """Public landing page with training calendar."""
    now = datetime.now()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))

    # Build calendar grid
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Fetch events for current month
    events = TrainingEvent.objects.filter(
        date__year=year,
        date__month=month
    ).order_by('date')

    event_days = {e.date.day: e.title for e in events}
    event_day_list = list(event_days.keys())

    prev_month = 12 if month == 1 else month - 1
    next_month = 1 if month == 12 else month + 1
    prev_year = year - 1 if month == 1 else year
    next_year = year + 1 if month == 12 else year

    context = {
        'cal': cal,
        'month_name': month_name,
        'month': month,
        'year': year,
        'prev_month': prev_month,
        'next_month': next_month,
        'prev_year': prev_year,
        'next_year': next_year,
        'event_days': event_days,
        'event_day_list': event_day_list,
        'events': events,
        'today': now.day,
        'current_month': now.month,
    }
    return render(request, 'public/index.html', context)


def book_service(request):
    """View to handle consultation and service inquiries."""
    tier = request.GET.get('tier', '')
    
    # Map tier param to models
    initial_data = {}
    if tier == 'Basic':
        initial_data['service_requested'] = 'ENROLL_BASIC'
    elif tier == 'Standard':
        initial_data['service_requested'] = 'ENROLL_STANDARD'
    elif tier == 'Premium':
        initial_data['service_requested'] = 'ENROLL_PREMIUM'

    if request.method == 'POST':
        form = ServiceInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            if request.user.is_authenticated:
                inquiry.user = request.user
            inquiry.save()
            return redirect('book_service_success')
    else:
        form = ServiceInquiryForm(initial=initial_data)
    
    return render(request, 'public/service_booking.html', {'form': form})


def book_service_success(request):
    """View rendered after a successful booking."""
    return render(request, 'public/service_success.html')


def public_courses(request):
    """Showcase of all offered courses with tiered pricing."""
    return render(request, 'public/courses.html', {
        'page_title': 'Language Programs',
        'brand_context': 'Programs',
    })


def terms(request):
    """Public Terms & Conditions page."""
    return render(request, 'public/terms.html')
