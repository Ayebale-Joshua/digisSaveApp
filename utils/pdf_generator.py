import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFGenerator:
    @staticmethod
    def generate_meeting_summary_pdf(meeting_data: dict, transactions: list, filepath: str) -> str:
        """
        Generates an A4-formatted PDF summary report for a specific VSLA meeting.
        """
        doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        story = []
        styles = getSampleStyleSheet()
        
        # Title Style
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=10,
            alignment=1 # Center
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#4A5568"),
            spaceAfter=20,
            alignment=1
        )

        story.append(Paragraph("DIGISAVE - VSLA MEETING SUMMARY REPORT", title_style))
        story.append(Paragraph(f"Meeting #{meeting_data.get('meeting_number')} | Date: {meeting_data.get('meeting_date')}", subtitle_style))
        story.append(Spacer(1, 10))

        # Financial Summary Table
        summary_data = [
            ["Total Cash In:", f"UGX {meeting_data.get('total_cash_in', 0.0):,.2f}"],
            ["Total Cash Out:", f"UGX {meeting_data.get('total_cash_out', 0.0):,.2f}"],
            ["Net Cash Box Balance:", f"UGX {(meeting_data.get('total_cash_in', 0.0) - meeting_data.get('total_cash_out', 0.0)):,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 300])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#2D3748")),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Transactions Table
        story.append(Paragraph("<b>Transaction Ledger Details</b>", styles['Heading2']))
        story.append(Spacer(1, 10))

        table_data = [["Passbook", "Member Name", "Type", "Source", "Amount (UGX)"]]
        for tx in transactions:
            table_data.append([
                str(tx.get("passbook_number")),
                str(tx.get("full_name")),
                str(tx.get("transaction_type")),
                str(tx.get("fund_source")),
                f"{tx.get('amount', 0.0):,.2f}"
            ])

        tx_table = Table(table_data, colWidths=[70, 150, 110, 80, 90])
        tx_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(tx_table)

        doc.build(story)
        return filepath