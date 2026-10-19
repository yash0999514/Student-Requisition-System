"""
Configuration and constants for the Student Academic Requisition System.
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
PDF_DIR = BASE_DIR / "generated_pdfs"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure runtime directories exist
for path in [DATA_DIR, UPLOADS_DIR, PDF_DIR, ASSETS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Database file location (uses DATA_DIR by default, or REQUISITION_DB_PATH if specified)
DB_PATH = Path(os.environ.get("REQUISITION_DB_PATH", str(DATA_DIR / "requisitions.db")))
CSV_BACKUP_PATH = DATA_DIR / "requisitions.csv"

# Academic Departments
DEPARTMENTS = [
    "Computer Engineering",
    "Information Technology",
    "Electronics & Telecommunication Engineering",
    "Artificial Intelligence & Data Science",
    "Mechanical Engineering",
    "Civil Engineering",
    "Electrical Engineering",
    "Chemical Engineering",
    "Applied Sciences & Humanities"
]

# Standard Application Types as per Institute Form
APPLICATION_TYPES = [
    "Bonafide",
    "Student Certificate",
    "Scholarship",
    "NOC",
    "Academic Permission",
    "Examination",
    "Internship",
    "Placement",
    "Other request"
]

# Semesters
SEMESTERS = [f"Semester {i}" for i in range(1, 9)]

# Divisions
DIVISIONS = ["A", "B", "C", "D", "E"]

# Application Statuses
STATUS_OPTIONS = [
    "Pending Verification",
    "Under HoD Review",
    "Forwarded to Cell/Authority",
    "Approved",
    "Not Approved",
    "Clarification Required"
]

# Forwarding Authorities listed in Section 5 of form
FORWARD_AUTHORITIES = [
    "VICE PRINCIPAL",
    "CHIEF ACADEMIC OFFICER",
    "ACCOUNTS",
    "SPORTS",
    "PLACEMENT CELL",
    "SCHOLARSHIP CELL",
    "EXAM CELL"
]

# Official Texts from Attached Form
PROCESSING_TIME_TEXT = (
    "Processing Time: The request will normally be processed within 4 working days "
    "after receiving the completed form and all required supporting documents. "
    "Students are advised to apply in advance, as incomplete applications may require "
    "additional processing time."
)

DECLARATION_TEXT = (
    "I certify that the information provided above is correct and that the request "
    "is being submitted for academic purposes. I understand that the request will "
    "be processed as per applicable Institute/University rules and within the "
    "stipulated processing time."
)

# App Metadata
APP_TITLE = "Student Academic Requisition Portal"
INSTITUTE_NAME = "Institute of Engineering & Technology"
ACADEMIC_YEAR = "2026-2027"
