"""
Validation module for student requisition inputs.
Provides robust checks for required fields, formats, regex matching, and business rules.
"""
import re
from typing import Dict, List, Tuple, Any

# Email validation regex conforming to RFC 5322 standard simplification
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

# Standard 10-digit mobile number validation (supports optional +91 or leading 0)
PHONE_REGEX = re.compile(
    r"^(?:\+91[-\s]?|0)?[6-9]\d{9}$"
)

# General international / flexible digits check (10 to 13 digits)
GENERIC_PHONE_DIGITS_REGEX = re.compile(
    r"^\+?\d{10,13}$"
)

# Roll Number alphanumeric check
ROLL_NO_REGEX = re.compile(
    r"^[A-Za-z0-9\-_/]{2,25}$"
)

def sanitize_name(name: str) -> str:
    """Sanitize string for safe filenames and system identifiers."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address format."""
    if not email or not isinstance(email, str):
        return False, "Email address is required."
    clean_email = email.strip()
    if not EMAIL_REGEX.match(clean_email):
        return False, "Please enter a valid email address (e.g., student@college.edu)."
    return True, ""

def validate_mobile(mobile: str) -> Tuple[bool, str]:
    """Validate phone/mobile number digits."""
    if not mobile or not isinstance(mobile, str):
        return False, "Mobile number is required."
    clean_mobile = mobile.strip().replace(" ", "").replace("-", "")
    if PHONE_REGEX.match(clean_mobile) or GENERIC_PHONE_DIGITS_REGEX.match(clean_mobile):
        return True, ""
    return False, "Mobile number must contain 10 valid digits (e.g., 9876543210)."

def validate_roll_number(roll_no: str) -> Tuple[bool, str]:
    """Validate roll number."""
    if not roll_no or not isinstance(roll_no, str):
        return False, "Roll number is required."
    clean_roll = roll_no.strip()
    if not ROLL_NO_REGEX.match(clean_roll):
        return False, "Roll number should be alphanumeric without special symbols (e.g., CS2023045)."
    return True, ""

def validate_name(name: str) -> Tuple[bool, str]:
    """Validate student full name."""
    if not name or not isinstance(name, str):
        return False, "Student name is required."
    clean_name = name.strip()
    if len(clean_name) < 2:
        return False, "Student name must be at least 2 characters long."
    if not re.match(r"^[A-Za-z\s.'\-]+$", clean_name):
        return False, "Student name should contain only alphabets, spaces, and dots."
    return True, ""

def validate_requisition_form(data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
    """
    Validate all fields of the student academic requisition form.
    Returns:
        (is_valid, errors_dict)
    """
    errors: Dict[str, str] = {}

    # Department
    dept = data.get("department", "").strip()
    if not dept:
        errors["department"] = "Department selection is mandatory."

    # Student Name
    name_ok, name_msg = validate_name(data.get("student_name", ""))
    if not name_ok:
        errors["student_name"] = name_msg

    # Roll Number
    roll_ok, roll_msg = validate_roll_number(data.get("roll_number", ""))
    if not roll_ok:
        errors["roll_number"] = roll_msg

    # Semester
    sem = str(data.get("semester", "")).strip()
    if not sem:
        errors["semester"] = "Semester is mandatory."

    # Division
    div = str(data.get("division", "")).strip()
    if not div:
        errors["division"] = "Division is mandatory."

    # Email
    email_ok, email_msg = validate_email(data.get("email", ""))
    if not email_ok:
        errors["email"] = email_msg

    # Mobile
    mob_ok, mob_msg = validate_mobile(data.get("mobile", ""))
    if not mob_ok:
        errors["mobile"] = mob_msg

    # Application Type
    app_type = data.get("application_type", "").strip()
    if not app_type:
        errors["application_type"] = "Please select an application type."
    elif app_type == "Other request":
        other_detail = data.get("other_application_type", "").strip()
        if not other_detail:
            errors["other_application_type"] = "Please specify details for 'Other request'."

    # Purpose / Brief Details of Request
    purpose = data.get("purpose", "").strip()
    if not purpose:
        errors["purpose"] = "Purpose / brief details of request is mandatory."
    elif len(purpose) < 10:
        errors["purpose"] = "Purpose must be at least 10 characters explaining your request."

    # Supporting Documents
    docs_attached = data.get("docs_attached", False)
    if docs_attached:
        doc_names = data.get("doc_names", "").strip()
        if not doc_names:
            errors["doc_names"] = "Please specify the names of attached supporting documents."

    # Student Declaration
    declaration_accepted = data.get("declaration_accepted", False)
    if not declaration_accepted:
        errors["declaration_accepted"] = "You must read and accept the Student Declaration to proceed."

    # Date
    submission_date = data.get("submission_date")
    if not submission_date:
        errors["submission_date"] = "Submission date is required."

    is_valid = len(errors) == 0
    return is_valid, errors
