# Daily Startup Protocol

This protocol serves as the standard operating procedure for beginning any new development session.

## 1. Create Startup Report
- **Mandatory Reporting**: Every time the system starts up, create a new report in the `protocol/daily_logs/{YYYY-MM-DD}/` directory.
- **Report Content**: Include local server status, live server status (if applicable), and any critical findings from the previous session.

## 2. Review Previous Daily Logs
- Check the most recent entries in the daily logs to identify what was being worked on previously.
- Understand the context, active bugs, and features in progress so we can seamlessly continue where we left off.

## 3. Verify Environment Status
- **Local Server Status**: Ensure the local development server is running properly (e.g., `python manage.py runserver 3002`).
- **Live Server Status**: Monitor the status of the live/production server to ascertain if there are any immediate production issues that need prioritization.

## 4. Identify and Execute Next Steps
- Based on the previous logs and any pending tasks, prioritize the work for the current session.
- Track progress in the current daily log for tomorrow's review.
