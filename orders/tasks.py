"""
Celery tasks for abandoned cart email automation.
This file can be used with Celery for automated task scheduling.
"""

from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_abandoned_cart_emails():
    """
    Celery task to send abandoned cart reminder emails.
    This task should be scheduled to run every hour.
    """
    try:
        call_command('send_abandoned_cart_emails')
        logger.info("Abandoned cart emails sent successfully")
        return "Abandoned cart emails sent successfully"
    except Exception as e:
        logger.error(f"Error sending abandoned cart emails: {str(e)}")
        raise e


# Alternative: Simple cron job command
# Add this to your crontab to run every hour:
# 0 * * * * cd /path/to/your/project && python manage.py send_abandoned_cart_emails

# For Windows Task Scheduler, create a batch file:
# @echo off
# cd "C:\path\to\your\project"
# python manage.py send_abandoned_cart_emails
