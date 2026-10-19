"""
PDF generation module for Student Academic Requisition Form.
Strictly reproduces the layout, typography, and sections of the official Institute form:
'Student Academic Requiste Form- 2026_New (1) (1).docx'
"""
import os
import io
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from PIL import Image as PILImage

from config import (
    PDF_DIR, PROCESSING_TIME_TEXT, DECLARATION_TEXT,
    FORWARD_AUTHORITIES, APPLICATION_TYPES
)

class SinglePageCanvas(canvas.Canvas):
    """Custom canvas ensuring strict single page bounding and metadata."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for page in self.pages:
            self.__dict__.update(page)
            super().showPage()
        super().save()

def sanitize_filename(name: str) -> str:
    """Sanitize string for safe filenames."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')

def generate_requisition_pdf(data: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Generate the official Student Academic Requisition Form PDF.
    
    Parameters:
        data: Dict containing student and application fields:
            - department (str)
            - requisition_no (str)
            - submission_date (str/date)
            - student_name (str)
            - roll_number (str)
            - semester (str)
            - division (str)
            - email (str)
            - mobile (str)
            - application_type (str)
            - other_application_type (str, optional)
            - purpose (str)
            - docs_attached (bool)
            - doc_names (str)
            - signature_path (str, optional)
        output_path: Optional custom destination file path.
        
    Returns:
        Absolute path of the generated PDF.
    """
    roll_no = sanitize_filename(data.get("roll_number", "RollNo"))
    student_name = sanitize_filename(data.get("student_name", "Student"))
    
    if not output_path:
        filename = f"Requisition_{roll_no}_{student_name}.pdf"
        output_path = str(PDF_DIR / filename)
    else:
        filename = os.path.basename(output_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # A4 dimensions: 595.27 x 841.89 points
    # Margins matching docx: Left 49.65pt, Right 49.55pt, Top 54pt, Bottom 42.5pt
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=49.65,
        rightMargin=49.55,
        topMargin=54.0,
        bottomMargin=42.0
    )

    usable_width = A4[0] - doc.leftMargin - doc.rightMargin  # 496.07 pt

    styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        'FormBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=colors.black
    )

    header_style = ParagraphStyle(
        'FormHeader',
        parent=body_style,
        fontSize=9.5,
        leading=13.5
    )

    header_right = ParagraphStyle(
        'FormHeaderRight',
        parent=header_style,
        alignment=TA_RIGHT
    )

    justify_style = ParagraphStyle(
        'FormJustify',
        parent=body_style,
        alignment=TA_JUSTIFY,
        leading=14.5
    )

    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.black
    )

    right_style = ParagraphStyle(
        'RightStyle',
        parent=body_style,
        alignment=TA_RIGHT
    )

    story = []

    # -------------------------------------------------------------
    # HEADER LINE: Department, Outward No, Date
    # -------------------------------------------------------------
    dept_val = data.get("department", "________________")
    outward_val = data.get("requisition_no", "________________")
    date_val = str(data.get("submission_date", datetime.date.today().strftime("%d/%m/%Y")))

    header_table_data = [
        [
            Paragraph(f"<b>Name of the Department.:</b> {dept_val}", header_style),
            Paragraph(f"<b>Department Outward No.:</b> {outward_val}", header_style),
            Paragraph(f"<b>Date:</b> {date_val}", header_right)
        ]
    ]
    # Balanced widths: 46%, 39%, 15% with 9.5pt ensures zero wrapping across all 3 items
    header_table = Table(
        header_table_data,
        colWidths=[usable_width * 0.46, usable_width * 0.39, usable_width * 0.15]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # PROCESSING TIME NOTICE
    # -------------------------------------------------------------
    proc_html = (
        f"<b>Processing Time:</b> The request will normally be processed within 4 working days "
        f"after receiving the completed form and all required supporting documents. "
        f"Students are advised to apply in advance, as incomplete applications may require "
        f"additional processing time."
    )
    story.append(Paragraph(proc_html, justify_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 1. STUDENT DETAILS
    # -------------------------------------------------------------
    story.append(Paragraph("1. STUDENT DETAILS", section_heading_style))

    student_name_val = data.get("student_name", "")
    roll_val = data.get("roll_number", "")
    sem_val = data.get("semester", "")
    div_val = data.get("division", "")
    email_val = data.get("email", "")
    mob_val = data.get("mobile", "")
    app_type_val = data.get("application_type", "")
    other_type_val = data.get("other_application_type", "")

    # Line 1: Name of Student
    story.append(Paragraph(f"Name of Student: &nbsp;<b>{student_name_val}</b>", body_style))
    story.append(Spacer(1, 3))

    # Line 2: Roll No, Semester, Division
    stud_line2_data = [
        [
            Paragraph(f"Roll No.: &nbsp;<b>{roll_val}</b>", body_style),
            Paragraph(f"Semester: &nbsp;<b>{sem_val}</b>", body_style),
            Paragraph(f"Division: &nbsp;<b>{div_val}</b>", body_style),
        ]
    ]
    stud_line2_table = Table(
        stud_line2_data,
        colWidths=[usable_width * 0.40, usable_width * 0.36, usable_width * 0.24]
    )
    stud_line2_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(stud_line2_table)
    story.append(Spacer(1, 3))

    # Line 3: Email / Mobile
    story.append(Paragraph(f"Email / Mobile: &nbsp;<b>{email_val}</b> &nbsp;/&nbsp; <b>{mob_val}</b>", body_style))
    story.append(Spacer(1, 3))

    # Line 4: Application for options
    app_types_raw = [
        "Bonafide", "Student Certificate", "Scholarship", "NOC",
        "Academic Permission", "Examination", "Internship", "Placement", "Other request"
    ]
    formatted_types = []
    for at in app_types_raw:
        if at.lower() == app_type_val.lower() or (at.lower() in app_type_val.lower() and len(at) > 3):
            formatted_types.append(f"<b><u>{at} [✓]</u></b>")
        else:
            formatted_types.append(at)
    
    app_options_text = " / ".join(formatted_types)
    app_line_html = f"Application for – {app_options_text}"
    if app_type_val.lower() == "other request" and other_type_val:
        app_line_html += f" &nbsp;(Specified: <i>{other_type_val}</i>)"
    story.append(Paragraph(app_line_html, body_style))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 2. PURPOSE / BRIEF DETAILS OF REQUEST
    # -------------------------------------------------------------
    story.append(Paragraph("2. PURPOSE / BRIEF DETAILS OF REQUEST", section_heading_style))
    purpose_val = data.get("purpose", "").strip()
    if purpose_val:
        story.append(Paragraph(f"{purpose_val}", ParagraphStyle('PurposeText', parent=body_style, leading=14.5)))
    else:
        story.append(Paragraph("<u>" + "&nbsp;" * 130 + "</u>", body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<u>" + "&nbsp;" * 130 + "</u>", body_style))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 3. SUPPORTING DOCUMENTS
    # -------------------------------------------------------------
    story.append(Paragraph("3. SUPPORTING DOCUMENTS", section_heading_style))
    docs_attached = bool(data.get("docs_attached", False))
    yes_mark = "[✓]" if docs_attached else "[ &nbsp; ]"
    no_mark = "[✓]" if not docs_attached else "[ &nbsp; ]"

    doc_attach_line = f"Documents attached: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>{yes_mark} Yes</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>{no_mark} No</b>"
    story.append(Paragraph(doc_attach_line, body_style))
    story.append(Spacer(1, 3))

    doc_names_val = data.get("doc_names", "").strip() or "N/A"
    story.append(Paragraph(f"Document name(s), if applicable: &nbsp;<b>{doc_names_val}</b>", body_style))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 4. STUDENT DECLARATION
    # -------------------------------------------------------------
    story.append(Paragraph("4. STUDENT DECLARATION", section_heading_style))
    decl_html = (
        "I certify that the information provided above is correct and that the request "
        "is being submitted for academic purposes. I understand that the request will "
        "be processed as per applicable Institute/University rules and within the "
        "stipulated processing time."
    )
    story.append(Paragraph(decl_html, justify_style))
    story.append(Spacer(1, 6))

    # Student Signature & Date Table
    sig_path = data.get("signature_path")
    has_valid_sig = sig_path and os.path.exists(sig_path)

    if has_valid_sig:
        try:
            with PILImage.open(sig_path) as pimg:
                w, h = pimg.size
                aspect = h / w if w > 0 else 0.3
            sig_w = 110
            sig_h = min(28, sig_w * aspect)
            sig_element = RLImage(sig_path, width=sig_w, height=sig_h)
        except Exception:
            sig_element = Paragraph("<u>_________________________</u>", body_style)
    else:
        sig_element = Paragraph("<u>_________________________</u>", body_style)

    sig_date_table_data = [
        [
            Paragraph("Student Signature:", body_style),
            sig_element,
            Paragraph(f"Date: &nbsp;<b>{date_val}</b>", right_style)
        ]
    ]
    sig_date_table = Table(
        sig_date_table_data,
        colWidths=[usable_width * 0.24, usable_width * 0.44, usable_width * 0.32]
    )
    sig_date_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(sig_date_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 5. HoD SIGNATURE & REMARKS (Official Use - Left Blank)
    # -------------------------------------------------------------
    hod_line1_data = [
        [
            Paragraph("<b>5. HoD Signature:</b> &nbsp;<u>_________________________</u>", body_style),
            Paragraph("<b>Remarks:</b> &nbsp;<u>_________________________________</u>", right_style)
        ]
    ]
    hod_line1_table = Table(hod_line1_data, colWidths=[usable_width * 0.52, usable_width * 0.48])
    hod_line1_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    story.append(hod_line1_table)
    story.append(Spacer(1, 4))

    fwd_text = (
        "Forwarded to (VICE PRINCIPAL/ CHIEF ACADEMIC OFFICER/ ACCOUNTS/ SPORTS/ "
        "PLACEMENT CELL/ SCHOLARSHIP CELL/ EXAM CELL) (if required)"
    )
    story.append(Paragraph(fwd_text, justify_style))
    story.append(Spacer(1, 4))

    fwd_sig_data = [
        [
            Paragraph("<b>Signature:</b> &nbsp;<u>_________________________</u>", body_style),
            Paragraph("<b>Remarks:</b> &nbsp;<u>_________________________________</u>", right_style)
        ]
    ]
    fwd_sig_table = Table(fwd_sig_data, colWidths=[usable_width * 0.52, usable_width * 0.48])
    fwd_sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    story.append(fwd_sig_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 6. PRINCIPAL OFFICE USE ONLY (Official Use - Left Blank)
    # -------------------------------------------------------------
    story.append(Paragraph("6. PRINCIPAL OFFICE USE ONLY", section_heading_style))

    decision_html = (
        "Decision by Principal.: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        "[ &nbsp; ] Approved &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        "[ &nbsp; ] Not Approved &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        "[ &nbsp; ] Clarification Required"
    )
    story.append(Paragraph(decision_html, body_style))
    story.append(Spacer(1, 5))

    remarks_line = (
        "Remarks (if any): &nbsp;"
        "<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>"
    )
    story.append(Paragraph(remarks_line, body_style))
    story.append(Spacer(1, 5))

    story.append(Paragraph("Principal Signature: &nbsp;<u>_________________________________</u>", body_style))

    # Build document
    doc.build(story, canvasmaker=SinglePageCanvas)
    return output_path
