"""
Core Utility Functions.

Shared helper functions used across the entire project:
- QR code generation
- PDF generation helpers
- Excel export helpers
- Token generation
- Time formatting
"""
import io
import logging
import os
import uuid
from datetime import datetime

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

logger = logging.getLogger('apps')


def generate_qr_code(data, filename=None):
    """
    Generate a QR code image from the given data.

    Args:
        data (str): The data to encode in the QR code.
        filename (str, optional): Custom filename. Auto-generated if not provided.

    Returns:
        ContentFile: A Django ContentFile containing the QR code PNG image.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Create the QR code image with brand colors
        img = qr.make_image(fill_color='#1a1a2e', back_color='white')

        # Save to buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')  # type: ignore
        buffer.seek(0)

        if not filename:
            filename = f'qr_{uuid.uuid4().hex[:8]}.png'

        return ContentFile(buffer.getvalue(), name=filename)

    except Exception as e:
        logger.error(f'QR code generation failed: {e}')
        return None


def generate_token_number(prefix, current_number):
    """
    Generate a formatted token number.

    Args:
        prefix (str): The service prefix (e.g., 'A', 'B', 'C').
        current_number (int): The current sequential number.

    Returns:
        str: Formatted token number (e.g., 'A-001', 'B-042').
    """
    return f'{prefix}-{current_number:03d}'


def format_wait_time(minutes):
    """
    Format minutes into a human-readable wait time string.

    Args:
        minutes (int): Number of minutes.

    Returns:
        str: Formatted string (e.g., '1 hr 30 min', '45 min').
    """
    if minutes is None or minutes <= 0:
        return 'No wait'

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours > 0 and remaining_minutes > 0:
        return f'{hours} hr {remaining_minutes} min'
    elif hours > 0:
        return f'{hours} hr'
    else:
        return f'{remaining_minutes} min'


def get_sri_lanka_time():
    """
    Get the current time in Sri Lanka timezone (Asia/Colombo).

    Returns:
        datetime: Current datetime in Sri Lanka timezone.
    """
    return timezone.now()


def get_today_date():
    """
    Get today's date in Sri Lanka timezone.

    Returns:
        date: Today's date.
    """
    return timezone.now().date()


def generate_unique_code(length=8):
    """
    Generate a unique alphanumeric code.

    Args:
        length (int): Length of the code (default: 8).

    Returns:
        str: Uppercase alphanumeric code.
    """
    return uuid.uuid4().hex[:length].upper()


def ensure_media_directory(subdirectory):
    """
    Ensure a subdirectory exists within the media root.

    Args:
        subdirectory (str): The subdirectory path relative to MEDIA_ROOT.

    Returns:
        str: Full path to the directory.
    """
    full_path = os.path.join(settings.MEDIA_ROOT or '', subdirectory)
    os.makedirs(full_path, exist_ok=True)
    return full_path


def calculate_estimated_wait_time(position, avg_service_time):
    """
    Calculate estimated wait time based on queue position.

    Args:
        position (int): Current position in the queue.
        avg_service_time (int): Average service time in minutes.

    Returns:
        int: Estimated wait time in minutes.
    """
    if position <= 0:
        return 0
    return (position - 1) * avg_service_time
