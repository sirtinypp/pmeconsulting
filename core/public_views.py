import calendar
from datetime import datetime
from django.shortcuts import render
from learning.models import TrainingEvent


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
    ).values('date', 'title')

    event_days = {e['date'].day: e['title'] for e in events}

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
        'today': now.day,
    }
    return render(request, 'public/index.html', context)
