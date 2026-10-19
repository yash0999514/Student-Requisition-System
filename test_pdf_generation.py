"""
Test script to generate a sample requisition PDF and check page count and layout.
"""
import sys
import pypdf
import pypdfium2 as pdfium
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdf_generator import generate_requisition_pdf
from config import BASE_DIR, PDF_DIR

sample_data = {
    "department": "Computer Engineering",
    "requisition_no": "REQ-2026-0045",
    "submission_date": "11/10/2026",
    "student_name": "Aarav Sharma",
    "roll_number": "CS2023045",
    "semester": "Semester 6",
    "division": "A",
    "email": "aarav.sharma@college.edu",
    "mobile": "9876543210",
    "application_type": "Bonafide",
    "other_application_type": "",
    "purpose": "Required for National Scholarship Portal (NSP) verification and state education loan renewal for academic year 2026-27.",
    "docs_attached": True,
    "doc_names": "Fee Receipt 2026, College Identity Card, Previous Year Marksheet",
    "declaration_accepted": True
}

out_pdf = str(PDF_DIR / "Requisition_CS2023045_Aarav_Sharma.pdf")
generate_requisition_pdf(sample_data, out_pdf)

# Check page count
reader = pypdf.PdfReader(out_pdf)
print(f"Generated PDF: {out_pdf}")
print(f"Total Pages: {len(reader.pages)}")

# Render preview to intermediate PNG in assets directory
preview_img_path = BASE_DIR / "assets" / "sample_requisition_preview.png"
pdf_doc = pdfium.PdfDocument(out_pdf)
for i, page in enumerate(pdf_doc, start=1):
    img_path = BASE_DIR / "assets" / f"sample_requisition_page_{i}.png"
    page.render(scale=2).to_pil().save(str(img_path))
    print(f"Rendered preview image: {img_path}")
pdf_doc.close()
