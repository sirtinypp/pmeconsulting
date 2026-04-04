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
    initial_service = request.GET.get('service', '')
    if request.method == 'POST':
        form = ServiceInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_service_success')
    else:
        # Map URL params to exact choices
        service_map = {
            'deep-analysis': 'DEEP_ANALYSIS',
            'cv-letter': 'CV_LETTER',
            'checklist': 'CHECKLIST',
            'follow-up': 'FOLLOW_UP',
        }
        mapped_val = service_map.get(initial_service, '')
        form = ServiceInquiryForm(initial={'service_requested': mapped_val})

    return render(request, 'public/service_booking.html', {'form': form})


def book_service_success(request):
    """View rendered after a successful booking."""
    return render(request, 'public/service_success.html')
