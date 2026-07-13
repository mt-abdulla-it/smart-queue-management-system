"""
Reports Views.
Handles Excel and PDF report generation for Queue Tokens.
"""
from typing import Any
import io
import openpyxl
from datetime import datetime

from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from apps.core.mixins import RoleRequiredMixin
from apps.queues.models import QueueToken

class ExportExcelView(RoleRequiredMixin, View):
    allowed_roles = ['ADMIN']
    
    def get(self, request, *args, **kwargs):
        # Create an Excel workbook
        wb = openpyxl.Workbook()
        ws: Any = wb.active
        ws.title = "Queue Tokens Report"
        
        # Headers
        headers = ['Token Number', 'User Name', 'Branch', 'Service', 'Status', 'Date Issued']
        ws.append(headers)
        
        # Fetch Data
        tokens = QueueToken.objects.all().select_related('user', 'service__department__branch').order_by('-created_at')
        
        for token in tokens:
            ws.append([
                token.token_number,
                token.user.get_full_name() if token.user else "Walk-in",
                token.service.department.branch.name,
                token.service.name,
                token.status,
                token.created_at.strftime('%Y-%m-%d %H:%M')
            ])
            
        # Prepare Response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="SQMS_Report_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        wb.save(response)
        
        return response


class ExportPDFView(RoleRequiredMixin, View):
    allowed_roles = ['ADMIN']
    
    def get(self, request, *args, **kwargs):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        elements = []
        
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Smart Queue Management System - Activity Report", styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Table Data
        data = [['Token Number', 'User Name', 'Service', 'Status', 'Date']]
        tokens = QueueToken.objects.all().select_related('user', 'service').order_by('-created_at')[:50] # Limit to 50 for PDF
        
        for token in tokens:
            data.append([
                token.token_number,
                token.user.get_full_name() if token.user else "Walk-in",
                token.service.name,
                token.status,
                token.created_at.strftime('%Y-%m-%d %H:%M')
            ])
            
        # Build Table
        t = Table(data, colWidths=[80, 120, 150, 80, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(t)
        doc.build(elements)
        
        # Return Response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="SQMS_Report_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response
