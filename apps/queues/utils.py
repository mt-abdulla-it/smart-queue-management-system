"""
Queue Utilities.

Generates QR codes and PDF tokens.
"""
import qrcode
import io
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_qr_code(data):
    """
    Generates a QR code image from the given string data.
    Returns a ContentFile that can be saved to an ImageField.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    
    return ContentFile(buffer.getvalue())

def generate_pdf_token(token):
    """
    Generates a PDF representation of the queue token.
    Returns a bytes buffer containing the PDF.
    """
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)
    
    p.setFont("Helvetica-Bold", 24)
    p.drawString(1 * inch, 10.5 * inch, f"{settings.SITE_NAME} - Queue Token")
    
    p.setFont("Helvetica", 14)
    p.drawString(1 * inch, 10 * inch, f"Branch: {token.service.department.branch.name}")
    p.drawString(1 * inch, 9.5 * inch, f"Department: {token.service.department.name}")
    p.drawString(1 * inch, 9 * inch, f"Service: {token.service.name}")
    
    p.setFont("Helvetica-Bold", 36)
    p.drawString(1 * inch, 8 * inch, f"Token: {token.token_number}")
    
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, 7 * inch, f"Date: {token.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    if token.qr_code:
        # reportlab can draw images
        try:
            p.drawImage(token.qr_code.path, 1 * inch, 4 * inch, width=3 * inch, height=3 * inch)
        except Exception:
            p.drawString(1 * inch, 6 * inch, "[QR Code Image Unavailable]")
            
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
