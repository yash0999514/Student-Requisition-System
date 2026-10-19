"""
Database access layer for Student Academic Requisition System.
Manages SQLite operations, auto-incrementing requisition IDs, status tracking, and reporting.
Also automatically maintains a CSV file to satisfy both SQLite and CSV storage requirements.
"""
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from config import DB_PATH, CSV_BACKUP_PATH

def get_connection() -> sqlite3.Connection:
    """Establish connection to SQLite database with Row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def sync_to_csv():
    """Syncs the entire SQLite table to CSV format for portability and backup."""
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM requisitions ORDER BY id ASC", conn)
            df.to_csv(str(CSV_BACKUP_PATH), index=False)
    except Exception as e:
        pass

def init_db():
    """Initialize database tables and indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requisitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requisition_no TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                student_name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                semester TEXT NOT NULL,
                division TEXT NOT NULL,
                email TEXT NOT NULL,
                mobile TEXT NOT NULL,
                application_type TEXT NOT NULL,
                other_application_type TEXT,
                purpose TEXT NOT NULL,
                docs_attached INTEGER NOT NULL DEFAULT 0,
                doc_names TEXT,
                supporting_doc_path TEXT,
                signature_path TEXT,
                submission_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending Verification',
                hod_remarks TEXT,
                forwarded_to TEXT,
                principal_decision TEXT,
                principal_remarks TEXT,
                pdf_filename TEXT,
                pdf_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_roll_number ON requisitions(roll_number);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_requisition_no ON requisitions(requisition_no);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_department ON requisitions(department);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON requisitions(status);")
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM requisitions;")
        if cursor.fetchone()[0] == 0:
            seed_data = [
                ("REQ-2026-0041", "Mechanical Engineering", "Sahil Kulkarni", "ME2023055", "Semester 4", "B", "sahil.k@college.edu", "9820112233", "Examination", "", "Special examination permission due to medical leave during mid-term exams.", 1, "Medical Fitness Certificate, Hospital Discharge Summary", "", "", "08/10/2026", "Clarification Required", "Medical certificate requires validation from civil surgeon.", None, None, "Pending doctor verification"),
                ("REQ-2026-0042", "Electronics & Telecommunication Engineering", "Ananya Iyer", "ET2023034", "Semester 6", "A", "ananya.i@college.edu", "9833445566", "NOC", "", "No Objection Certificate required for participating in Smart India Hackathon grand finale at IIT Kharagpur.", 1, "Invitation Letter, Team Selection Proof", "", "", "09/10/2026", "Approved", "Verified project submission and team details. Recommended.", "VICE PRINCIPAL", "Approved", "Sanctioned on-duty leave for 4 days."),
                ("REQ-2026-0043", "Information Technology", "Rohan Verma", "IT2023012", "Semester 4", "A", "rohan.v@college.edu", "9123456780", "Scholarship", "", "State government post-matric scholarship renewal and income documentation verification.", 1, "Income Certificate, Fee Receipt", "", "", "09/10/2026", "Under HoD Review", "Documents under review by department coordinator.", "SCHOLARSHIP CELL", None, None),
                ("REQ-2026-0044", "Computer Engineering", "Pooja Deshmukh", "CS2023089", "Semester 8", "B", "pooja.d@college.edu", "9765432109", "Internship", "", "Permission and NOC for 6-month industrial internship at Microsoft IDC.", 1, "Internship Offer Letter, NDA Document", "", "", "10/10/2026", "Approved", "Offer letter verified. Attendance criteria satisfied.", "PLACEMENT CELL", "Approved", "Approved as per institute internship policy."),
                ("REQ-2026-0045", "Computer Engineering", "Aarav Sharma", "CS2023045", "Semester 6", "A", "aarav.sharma@college.edu", "9876543210", "Bonafide", "", "Required for National Scholarship Portal (NSP) verification and state education loan renewal for academic year 2026-27.", 1, "Fee Receipt 2026, College Identity Card, Previous Year Marksheet", "", "", "11/10/2026", "Pending Verification", "Verified all enclosed documents. Recommended.", "VICE PRINCIPAL", "Approved", "Granted approval.")
            ]
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.executemany("""
                INSERT INTO requisitions (
                    requisition_no, department, student_name, roll_number,
                    semester, division, email, mobile,
                    application_type, other_application_type, purpose,
                    docs_attached, doc_names, supporting_doc_path, signature_path,
                    submission_date, status, hod_remarks, forwarded_to,
                    principal_decision, principal_remarks, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19], r[20], now_str, now_str) for r in seed_data])
            conn.commit()
    sync_to_csv()

def generate_next_requisition_number(conn: sqlite3.Connection) -> str:
    """Generate a unique formatted Requisition Number like REQ-2026-0001."""
    current_year = datetime.datetime.now().year
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM requisitions WHERE requisition_no LIKE ?", (f"REQ-{current_year}-%",))
    count = cursor.fetchone()[0]
    next_seq = count + 1
    return f"REQ-{current_year}-{next_seq:04d}"

def create_requisition(data: Dict[str, Any]) -> Tuple[int, str]:
    """
    Inserts a new requisition into the database.
    Returns (id, requisition_no).
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        req_no = generate_next_requisition_number(conn)

        cursor.execute("""
            INSERT INTO requisitions (
                requisition_no, department, student_name, roll_number,
                semester, division, email, mobile,
                application_type, other_application_type, purpose,
                docs_attached, doc_names, supporting_doc_path, signature_path,
                submission_date, status, pdf_filename, pdf_path,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            req_no,
            data.get("department", ""),
            data.get("student_name", ""),
            data.get("roll_number", ""),
            data.get("semester", ""),
            data.get("division", ""),
            data.get("email", ""),
            data.get("mobile", ""),
            data.get("application_type", ""),
            data.get("other_application_type", ""),
            data.get("purpose", ""),
            1 if data.get("docs_attached") else 0,
            data.get("doc_names", ""),
            data.get("supporting_doc_path", ""),
            data.get("signature_path", ""),
            data.get("submission_date", datetime.date.today().strftime("%d/%m/%Y")),
            data.get("status", "Pending Verification"),
            data.get("pdf_filename", ""),
            data.get("pdf_path", ""),
            now,
            now
        ))
        conn.commit()
        last_id = cursor.lastrowid

    sync_to_csv()
    return last_id, req_no

def update_requisition_pdf(requisition_no: str, pdf_filename: str, pdf_path: str):
    """Updates the PDF file reference for a requisition."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE requisitions
            SET pdf_filename = ?, pdf_path = ?, updated_at = ?
            WHERE requisition_no = ?
        """, (pdf_filename, pdf_path, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), requisition_no))
        conn.commit()
    sync_to_csv()

def get_requisition_by_id(req_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve single requisition by database ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requisitions WHERE id = ?", (req_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_requisition_by_no(req_no: str) -> Optional[Dict[str, Any]]:
    """Retrieve single requisition by Requisition Number."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requisitions WHERE requisition_no = ? COLLATE NOCASE", (req_no.strip(),))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_requisitions_by_roll_no(roll_no: str) -> List[Dict[str, Any]]:
    """Retrieve all requisitions submitted by a given Roll Number."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requisitions WHERE roll_number = ? COLLATE NOCASE ORDER BY id DESC", (roll_no.strip(),))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def get_all_requisitions(
    search_query: Optional[str] = None,
    dept_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    app_type_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Query requisitions with optional filters for search, department, and status."""
    query = "SELECT * FROM requisitions WHERE 1=1"
    params = []

    if search_query:
        query += " AND (requisition_no LIKE ? OR student_name LIKE ? OR roll_number LIKE ? OR email LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term, term, term])

    if dept_filter and dept_filter != "All":
        query += " AND department = ?"
        params.append(dept_filter)

    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    if app_type_filter and app_type_filter != "All":
        query += " AND application_type = ?"
        params.append(app_type_filter)

    query += " ORDER BY id DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def update_requisition_status(
    requisition_no: str,
    status: str,
    hod_remarks: Optional[str] = None,
    forwarded_to: Optional[str] = None,
    principal_decision: Optional[str] = None,
    principal_remarks: Optional[str] = None
) -> bool:
    """Updates administrative review fields and status."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE requisitions
            SET status = ?,
                hod_remarks = COALESCE(?, hod_remarks),
                forwarded_to = COALESCE(?, forwarded_to),
                principal_decision = COALESCE(?, principal_decision),
                principal_remarks = COALESCE(?, principal_remarks),
                updated_at = ?
            WHERE requisition_no = ?
        """, (status, hod_remarks, forwarded_to, principal_decision, principal_remarks, now, requisition_no))
        conn.commit()
        success = cursor.rowcount > 0

    sync_to_csv()
    return success

def get_summary_stats() -> Dict[str, int]:
    """Returns analytics metrics for dashboard."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM requisitions")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM requisitions WHERE status IN ('Pending Verification', 'Under HoD Review')")
        pending = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM requisitions WHERE status = 'Approved'")
        approved = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM requisitions WHERE status = 'Not Approved'")
        rejected = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM requisitions WHERE status = 'Clarification Required'")
        clarification = cursor.fetchone()[0]

        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "clarification": clarification
        }

def export_to_dataframe() -> pd.DataFrame:
    """Exports all requisitions as a Pandas DataFrame for CSV/Excel export."""
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM requisitions ORDER BY id DESC", conn)
        return df

# Initialize database on module import
init_db()
