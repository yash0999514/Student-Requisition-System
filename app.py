"""
Student Academic Requisition Portal
Streamlit web application for students, faculty, and administrators.
"""
import os
import sys
import datetime
from pathlib import Path
import streamlit as st
import pandas as pd

# Page Configuration - Hide sidebar by default
st.set_page_config(
    page_title="Student Academic Requisition Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import (
    DEPARTMENTS, APPLICATION_TYPES, SEMESTERS, DIVISIONS,
    STATUS_OPTIONS, FORWARD_AUTHORITIES, PROCESSING_TIME_TEXT,
    DECLARATION_TEXT, APP_TITLE, INSTITUTE_NAME, ACADEMIC_YEAR,
    UPLOADS_DIR, PDF_DIR
)
import database
import validator
from pdf_generator import generate_requisition_pdf

# -----------------------------------------------------------------------------
# Premium Custom Styling (Sidebar Hidden & Dark/Light Theme Aware)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* 1. COMPLETELY HIDE SIDEBAR & SIDEBAR CONTROLS */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 2. MODERN TYPOGRAPHY & LAYOUT */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 4rem;
        max-width: 1240px;
    }

    /* 3. TOP PORTAL HEADER */
    .portal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 24px;
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.15) 0%, rgba(59, 130, 246, 0.08) 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 14px;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }
    .portal-branding {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .portal-badge {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: #ffffff;
        font-weight: 800;
        font-size: 16px;
        padding: 10px 14px;
        border-radius: 10px;
        letter-spacing: 1px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    .portal-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--text-color, #f8fafc);
        margin: 0;
        line-height: 1.2;
    }
    .portal-subtitle {
        font-size: 13px;
        color: #94a3b8;
        margin: 3px 0 0 0;
    }
    .portal-chips {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    .portal-chip {
        display: inline-flex;
        align-items: center;
        padding: 5px 12px;
        font-size: 12px;
        font-weight: 600;
        border-radius: 9999px;
        background: rgba(148, 163, 184, 0.1);
        border: 1px solid rgba(148, 163, 184, 0.2);
        color: var(--text-color, #cbd5e1);
    }
    .portal-chip.active {
        background: rgba(16, 185, 129, 0.15);
        border-color: rgba(16, 185, 129, 0.35);
        color: #34d399;
    }

    /* 4. STREAMLIT TABS STYLING */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.4);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        padding: 0 20px;
        font-weight: 600;
        font-size: 14px;
        color: #94a3b8;
        border: none;
        background-color: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #f8fafc;
        background-color: rgba(255, 255, 255, 0.05);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    /* 5. METRIC CARDS */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 14px;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(8px);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
    }
    .metric-card.blue::before { background: #3b82f6; }
    .metric-card.amber::before { background: #f59e0b; }
    .metric-card.green::before { background: #10b981; }
    .metric-card.purple::before { background: #a855f7; }
    .metric-card.red::before { background: #f43f5e; }

    .metric-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        line-height: 1;
        color: #f8fafc;
    }

    /* 6. STATUS BADGES */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-align: center;
    }
    .badge-approved { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-pending { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-review { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-clarification { background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }
    .badge-rejected { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

    /* 7. SECTION PANELS */
    .section-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 15px;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* 8. NOTICE BOX */
    .notice-box {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .notice-box-text {
        font-size: 13px;
        color: #a7f3d0;
        line-height: 1.4;
    }

    /* 9. STEPPER PROGRESS */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        position: relative;
        margin: 20px 0 25px 0;
    }
    .stepper-container::before {
        content: '';
        position: absolute;
        top: 14px;
        left: 20px;
        right: 20px;
        height: 3px;
        background: rgba(148, 163, 184, 0.2);
        z-index: 1;
    }
    .step-item {
        position: relative;
        z-index: 2;
        text-align: center;
        flex: 1;
    }
    .step-circle {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #1e293b;
        border: 2px solid #64748b;
        color: #94a3b8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 700;
        margin: 0 auto 6px auto;
    }
    .step-item.active .step-circle {
        background: #2563eb;
        border-color: #60a5fa;
        color: #ffffff;
        box-shadow: 0 0 10px rgba(37, 99, 235, 0.5);
    }
    .step-item.completed .step-circle {
        background: #10b981;
        border-color: #34d399;
        color: #ffffff;
    }
    .step-text {
        font-size: 12px;
        font-weight: 600;
        color: #94a3b8;
    }
    .step-item.active .step-text {
        color: #60a5fa;
    }
    .step-item.completed .step-text {
        color: #34d399;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to get status badge HTML
def get_badge_markup(status: str) -> str:
    s = (status or "").lower()
    if "approved" in s and "not" not in s:
        cls = "badge-approved"
    elif "pending" in s:
        cls = "badge-pending"
    elif "hod" in s or "forwarded" in s or "review" in s:
        cls = "badge-review"
    elif "clarification" in s:
        cls = "badge-clarification"
    else:
        cls = "badge-rejected"
    return f'<span class="status-badge {cls}">{status}</span>'


# -----------------------------------------------------------------------------
# TOP PORTAL BRANDING & NAVIGATION HEADER
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="portal-header">
    <div class="portal-branding">
        <div class="portal-badge">IET</div>
        <div>
            <h1 class="portal-title">{INSTITUTE_NAME}</h1>
            <p class="portal-subtitle">{APP_TITLE} • Academic Year {ACADEMIC_YEAR}</p>
        </div>
    </div>
    <div class="portal-chips">
        <div class="portal-chip active">🟢 System Active</div>
        <div class="portal-chip">⚡ 4-Day SLA</div>
        <div class="portal-chip">🏛️ Vidyalankar Campus</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs (Top-Level Clean Bar)
tab_submit, tab_track, tab_admin, tab_policy = st.tabs([
    "📝  Submit Requisition Form",
    "🔍  Track Application Status",
    "📊  Administrative & HoD Portal",
    "📋  Guidelines & Format Policy"
])


# =============================================================================
# TAB 1: SUBMIT REQUISITION FORM
# =============================================================================
with tab_submit:
    st.markdown("""
    <div class="notice-box">
        <div style="font-size: 20px;">⏱️</div>
        <div class="notice-box-text">
            <strong>Standard Turnaround:</strong> Requisitions are processed within 4 working days of submitting required documents.
            Ensure correct personal details and valid enclosures are listed.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form(key="student_requisition_form", clear_on_submit=False):
        # 1. Academic & Department Info
        st.markdown('<div class="section-header">🏛️ 1. Academic & Department Information</div>', unsafe_allow_html=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            form_dept = st.selectbox("Academic Department *", options=DEPARTMENTS, index=0)
        with col_d2:
            current_date_str = datetime.date.today().strftime("%d/%m/%Y")
            form_date = st.text_input("Application Date *", value=current_date_str, help="Format: DD/MM/YYYY")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # 2. Student Details
        st.markdown('<div class="section-header">👤 2. Student Identification Details</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            form_name = st.text_input("Full Name of Student *", placeholder="e.g. Aarav Sharma")
        with col_s2:
            form_roll = st.text_input("Roll Number *", placeholder="e.g. CS2023045")

        col_sub1, col_sub2, col_sub3, col_sub4 = st.columns(4)
        with col_sub1:
            form_sem = st.selectbox("Semester *", options=SEMESTERS, index=5)
        with col_sub2:
            form_div = st.selectbox("Division *", options=DIVISIONS, index=0)
        with col_sub3:
            form_mob = st.text_input("Mobile Number *", placeholder="10-digit mobile number")
        with col_sub4:
            form_email = st.text_input("Email Address *", placeholder="e.g. aarav.sharma@college.edu")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # 3. Application Type & Details
        st.markdown('<div class="section-header">📄 3. Requisition Specification & Supporting Details</div>', unsafe_allow_html=True)
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            form_app_type = st.selectbox("Application For *", options=APPLICATION_TYPES, index=0)
        with col_t2:
            form_docs_attached = st.radio("Supporting Documents Attached? *", options=["Yes", "No"], horizontal=True, index=0)
            has_docs = (form_docs_attached == "Yes")

        form_other_desc = ""
        if form_app_type == "Other request":
            form_other_desc = st.text_input("Please specify custom requisition details *", placeholder="State request title...")

        form_doc_names = ""
        if has_docs:
            form_doc_names = st.text_input(
                "Names of Attached Documents *",
                value="Fee Receipt 2026, College Identity Card, Previous Year Marksheet",
                help="Enter document names separated by commas"
            )

        form_purpose = st.text_area(
            "Purpose / Detailed Justification of Request *",
            value="Required for National Scholarship Portal (NSP) verification and state education loan renewal for academic year 2026-27.",
            placeholder="Explain the academic reason and where this certificate/permission will be submitted...",
            height=95
        )

        with st.expander("📎 Optional Document & Digital Signature Enclosures", expanded=False):
            st.caption("You may upload digital PDF proof or an image of your signature.")
            up_col1, up_col2 = st.columns(2)
            with up_col1:
                uploaded_proof = st.file_uploader("Enclosed Proof (PDF / PNG / JPG)", type=["pdf", "png", "jpg", "jpeg"])
            with up_col2:
                uploaded_sig_img = st.file_uploader("Digital Signature (PNG / JPG)", type=["png", "jpg", "jpeg"])

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # 4. Student Declaration
        st.markdown('<div class="section-header">✍️ 4. Student Academic Declaration</div>', unsafe_allow_html=True)
        form_decl = st.checkbox(
            f"I certify that the information provided above is correct and submit this for academic purposes. (Declaration Accepted)",
            value=True
        )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 Submit Requisition & Generate Official PDF", type="primary", use_container_width=True)

    # Process Submission
    if submit_btn:
        submission_payload = {
            "department": form_dept,
            "submission_date": form_date,
            "student_name": form_name,
            "roll_number": form_roll,
            "semester": form_sem,
            "division": form_div,
            "email": form_email,
            "mobile": form_mob,
            "application_type": form_app_type,
            "other_application_type": form_other_desc,
            "purpose": form_purpose,
            "docs_attached": has_docs,
            "doc_names": form_doc_names,
            "declaration_accepted": form_decl
        }

        is_valid, validation_errors = validator.validate_requisition_form(submission_payload)

        if not is_valid:
            st.error("⚠️ Please resolve the following errors to complete your submission:")
            for field, err_text in validation_errors.items():
                st.markdown(f"- **{field.replace('_', ' ').title()}**: {err_text}")
        else:
            # Save uploaded files if provided
            if uploaded_proof is not None:
                dest_proof = UPLOADS_DIR / f"{validator.sanitize_name(form_roll)}_{uploaded_proof.name}"
                with open(dest_proof, "wb") as f:
                    f.write(uploaded_proof.getbuffer())
                submission_payload["supporting_doc_path"] = str(dest_proof)

            if uploaded_sig_img is not None:
                dest_sig = UPLOADS_DIR / f"sig_{validator.sanitize_name(form_roll)}_{uploaded_sig_img.name}"
                with open(dest_sig, "wb") as f:
                    f.write(uploaded_sig_img.getbuffer())
                submission_payload["signature_path"] = str(dest_sig)

            # Insert into database
            new_id, new_req_no = database.create_requisition(submission_payload)
            submission_payload["requisition_no"] = new_req_no

            # Generate official PDF form
            generated_pdf_file = generate_requisition_pdf(submission_payload)
            database.update_requisition_pdf(new_req_no, os.path.basename(generated_pdf_file), generated_pdf_file)

            st.session_state["submitted_req_no"] = new_req_no
            st.session_state["submitted_pdf_path"] = generated_pdf_file
            st.session_state["submitted_student"] = form_name
            st.session_state["submitted_roll"] = form_roll

            st.success(f"🎉 Application Registered! Assigned Reference ID: **{new_req_no}**")

    # Immediate download button if submission succeeded
    if "submitted_req_no" in st.session_state:
        req_ref = st.session_state["submitted_req_no"]
        fpath = st.session_state.get("submitted_pdf_path", "")
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                pdf_data = f.read()
            st.markdown("---")
            d_col1, d_col2 = st.columns([3, 1])
            with d_col1:
                st.info(f"✅ Requisition **{req_ref}** for {st.session_state.get('submitted_student')} ({st.session_state.get('submitted_roll')}) is compiled and ready.")
            with d_col2:
                st.download_button(
                    label=f"📥 Download PDF ({req_ref})",
                    data=pdf_data,
                    file_name=os.path.basename(fpath),
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )


# =============================================================================
# TAB 2: TRACK APPLICATION STATUS
# =============================================================================
with tab_track:
    st.markdown("### 🔍 Live Application Tracking")
    st.caption("Search using your Student Roll Number or unique Requisition ID to view endorsement status, HoD feedback, and principal approval.")

    tr_col1, tr_col2 = st.columns([3, 1])
    with tr_col1:
        track_query = st.text_input("Enter Roll Number or Requisition Number", placeholder="e.g. CS2023045 or REQ-2026-0045", label_visibility="collapsed")
    with tr_col2:
        track_search_clicked = st.button("Search Status", type="primary", use_container_width=True)

    clean_track = track_query.strip()
    if clean_track:
        matching_reqs = []
        if clean_track.upper().startswith("REQ-"):
            found = database.get_requisition_by_no(clean_track)
            if found:
                matching_reqs.append(found)
        else:
            matching_reqs = database.get_requisitions_by_roll_no(clean_track)
            if not matching_reqs:
                found = database.get_requisition_by_no(clean_track)
                if found:
                    matching_reqs.append(found)

        if not matching_reqs:
            st.warning(f"No records found for '{clean_track}'. Please double check your Roll Number or Requisition Number.")
        else:
            st.success(f"Found {len(matching_reqs)} requisition record(s) for **{clean_track}**")
            for item in matching_reqs:
                st_val = item.get("status", "Pending Verification")

                # Compute stepper active index
                # Steps: 1. Submitted -> 2. HoD Review -> 3. Authority Routing -> 4. Principal Decision
                s_lower = st_val.lower()
                step1_cls = "completed"
                step2_cls = "completed" if ("review" in s_lower or "forwarded" in s_lower or "approved" in s_lower or "not approved" in s_lower) else ("active" if "pending" in s_lower else "")
                step3_cls = "completed" if ("forwarded" in s_lower or "approved" in s_lower or "not approved" in s_lower) else ("active" if "review" in s_lower else "")
                step4_cls = "completed" if ("approved" in s_lower and "not" not in s_lower) else ("active" if ("not approved" in s_lower or "clarification" in s_lower) else "")

                st.markdown(f"""
                <div class="section-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(148, 163, 184, 0.15); padding-bottom: 12px; margin-bottom: 16px;">
                        <div>
                            <span style="font-size: 18px; font-weight: 800; color: #38bdf8;">{item['requisition_no']}</span>
                            <span style="font-size: 13px; color: #94a3b8; margin-left: 12px;">Submitted on {item['submission_date']}</span>
                        </div>
                        <div>
                            {get_badge_markup(st_val)}
                        </div>
                    </div>
                    
                    <div class="stepper-container">
                        <div class="step-item {step1_cls}">
                            <div class="step-circle">1</div>
                            <div class="step-text">Submitted</div>
                        </div>
                        <div class="step-item {step2_cls}">
                            <div class="step-circle">2</div>
                            <div class="step-text">HoD Review</div>
                        </div>
                        <div class="step-item {step3_cls}">
                            <div class="step-circle">3</div>
                            <div class="step-text">Cell Routing</div>
                        </div>
                        <div class="step-item {step4_cls}">
                            <div class="step-circle">4</div>
                            <div class="step-text">Principal Sanction</div>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; font-size: 13.5px; margin-bottom: 14px;">
                        <div><strong>Student:</strong> {item['student_name']}</div>
                        <div><strong>Roll Number:</strong> {item['roll_number']}</div>
                        <div><strong>Department:</strong> {item['department']}</div>
                        <div><strong>Class:</strong> {item['semester']} - {item['division']}</div>
                        <div><strong>Application Type:</strong> {item['application_type']}</div>
                        <div><strong>Enclosures:</strong> {item['doc_names'] or 'None'}</div>
                    </div>

                    <div style="background: rgba(15, 23, 42, 0.4); border-radius: 8px; padding: 12px 14px; font-size: 13.5px; margin-bottom: 14px; border: 1px solid rgba(148, 163, 184, 0.1);">
                        <strong>Purpose Statement:</strong> {item['purpose']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Processing notes row
                info_c1, info_c2, info_c3 = st.columns(3)
                with info_c1:
                    st.write(f"**HoD Remarks:** {item.get('hod_remarks') or 'Awaiting review'}")
                with info_c2:
                    st.write(f"**Forwarded Authority:** {item.get('forwarded_to') or 'Not forwarded'}")
                with info_c3:
                    st.write(f"**Principal Decision:** {item.get('principal_decision') or 'Pending'}")

                # Download PDF
                doc_path = item.get("pdf_path")
                if not doc_path or not os.path.exists(doc_path):
                    doc_path = generate_requisition_pdf(item)
                    database.update_requisition_pdf(item["requisition_no"], os.path.basename(doc_path), doc_path)

                if os.path.exists(doc_path):
                    with open(doc_path, "rb") as f:
                        file_bytes = f.read()
                    st.download_button(
                        label=f"⬇️ Download Official Requisition PDF ({item['requisition_no']})",
                        data=file_bytes,
                        file_name=f"Requisition_{item['roll_number']}_{item['student_name']}.pdf",
                        mime="application/pdf",
                        key=f"track_dl_{item['requisition_no']}"
                    )
                st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    else:
        st.info("💡 Enter your Student Roll Number (e.g. `CS2023045`) or Requisition Reference (e.g. `REQ-2026-0045`) above to track status.")


# =============================================================================
# TAB 3: ADMINISTRATIVE & HOD PORTAL
# =============================================================================
with tab_admin:
    st.markdown("### 📊 Administrative & Faculty Governance Portal")
    st.caption("Review submissions, register HoD recommendations, route to designated campus cells, and record principal decisions.")

    # High-level Analytics Metric Cards
    dash_stats = database.get_summary_stats()
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card blue">
            <div class="metric-label">Total Submissions</div>
            <div class="metric-value">{dash_stats['total']}</div>
        </div>
        <div class="metric-card amber">
            <div class="metric-label">Pending Review</div>
            <div class="metric-value">{dash_stats['pending']}</div>
        </div>
        <div class="metric-card green">
            <div class="metric-label">Approved</div>
            <div class="metric-value">{dash_stats['approved']}</div>
        </div>
        <div class="metric-card purple">
            <div class="metric-label">Clarification Needed</div>
            <div class="metric-value">{dash_stats['clarification']}</div>
        </div>
        <div class="metric-card red">
            <div class="metric-label">Not Approved</div>
            <div class="metric-value">{dash_stats['rejected']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filter Bar
    f_c1, f_c2, f_c3 = st.columns([2, 1, 1])
    with f_c1:
        query_filter = st.text_input("Search Registry", placeholder="Filter by Name, Roll No, Requisition ID...", label_visibility="collapsed")
    with f_c2:
        dept_sel = st.selectbox("Department", options=["All"] + DEPARTMENTS, label_visibility="collapsed")
    with f_c3:
        status_sel = st.selectbox("Status", options=["All"] + STATUS_OPTIONS, label_visibility="collapsed")

    all_requisitions = database.get_all_requisitions(
        search_query=query_filter,
        dept_filter=dept_sel,
        status_filter=status_sel
    )

    if not all_requisitions:
        st.info("No requisitions found matching current filter parameters.")
    else:
        # Build clean DataFrame for Streamlit's native Dark-mode aware table
        df_display = pd.DataFrame([
            {
                "Requisition ID": r["requisition_no"],
                "Student Name": r["student_name"],
                "Roll Number": r["roll_number"],
                "Department": r["department"],
                "Application Type": r["application_type"],
                "Submission Date": r["submission_date"],
                "Status": r["status"]
            }
            for r in all_requisitions
        ])

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Requisition ID": st.column_config.TextColumn("Requisition ID", width="small"),
                "Student Name": st.column_config.TextColumn("Student Name", width="medium"),
                "Roll Number": st.column_config.TextColumn("Roll Number", width="small"),
                "Department": st.column_config.TextColumn("Department", width="medium"),
                "Application Type": st.column_config.TextColumn("Type", width="small"),
                "Submission Date": st.column_config.TextColumn("Date", width="small"),
                "Status": st.column_config.TextColumn("Current Status", width="small"),
            }
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Action Review Panel
        st.markdown("### 📝 Application Review & Official Sanction")
        
        req_mapping = {
            f"{r['requisition_no']} — {r['student_name']} ({r['roll_number']}) [{r['status']}]": r['requisition_no']
            for r in all_requisitions
        }
        selected_option = st.selectbox("Select Application to Inspect & Endorse:", list(req_mapping.keys()))
        selected_req_id = req_mapping[selected_option]
        active_req = database.get_requisition_by_no(selected_req_id)

        if active_req:
            st.markdown(f"""
            <div class="section-card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(148, 163, 184, 0.15); padding-bottom: 10px; margin-bottom: 14px;">
                    <div>
                        <h4 style="margin: 0; color: #38bdf8;">Reviewing: {active_req['requisition_no']} ({active_req['student_name']})</h4>
                        <div style="font-size: 13px; color: #94a3b8;">{active_req['department']} • {active_req['semester']} ({active_req['division']}) • Roll: {active_req['roll_number']}</div>
                    </div>
                    <div>
                        {get_badge_markup(active_req['status'])}
                    </div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.4); padding: 12px 14px; border-radius: 8px; font-size: 13.5px; border: 1px solid rgba(148, 163, 184, 0.1);">
                    <strong>Purpose Statement:</strong> {active_req['purpose']}<br>
                    <strong>Enclosed Documents:</strong> {active_req['doc_names'] or 'None'}
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form(key=f"admin_review_form_{active_req['requisition_no']}"):
                rev_col1, rev_col2 = st.columns(2)
                with rev_col1:
                    updated_status = st.selectbox(
                        "Update Status *",
                        options=STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(active_req['status']) if active_req['status'] in STATUS_OPTIONS else 0
                    )
                    route_authority = st.selectbox(
                        "Route to Forwarding Authority (Section 5)",
                        options=["None"] + FORWARD_AUTHORITIES,
                        index=(FORWARD_AUTHORITIES.index(active_req['forwarded_to']) + 1) if active_req.get('forwarded_to') in FORWARD_AUTHORITIES else 0
                    )
                with rev_col2:
                    p_dec_options = ["Pending Decision", "Approved", "Not Approved", "Clarification Required"]
                    current_dec = active_req.get('principal_decision') or "Pending Decision"
                    dec_idx = p_dec_options.index(current_dec) if current_dec in p_dec_options else 0
                    principal_decision = st.selectbox(
                        "Principal Executive Decision (Section 6)",
                        options=p_dec_options,
                        index=dec_idx
                    )

                hod_remarks = st.text_area(
                    "HoD Verification & Remarks (Section 4)",
                    value=active_req.get("hod_remarks") or "",
                    placeholder="Enter verification comments and HoD endorsement..."
                )

                principal_remarks = st.text_area(
                    "Principal Office Remarks (Section 6)",
                    value=active_req.get("principal_remarks") or "",
                    placeholder="Official institute sanction remarks..."
                )

                save_decision_clicked = st.form_submit_button("💾 Save Official Decision & Update Status", type="primary", use_container_width=True)

            if save_decision_clicked:
                fwd_arg = None if route_authority == "None" else route_authority
                dec_arg = None if principal_decision == "Pending Decision" else principal_decision
                saved_ok = database.update_requisition_status(
                    requisition_no=active_req['requisition_no'],
                    status=updated_status,
                    hod_remarks=hod_remarks,
                    forwarded_to=fwd_arg,
                    principal_decision=dec_arg,
                    principal_remarks=principal_remarks
                )
                if saved_ok:
                    st.success(f"✅ Requisition {active_req['requisition_no']} successfully updated!")
                    st.rerun()
                else:
                    st.error("Could not update requisition.")

            # PDF Download for this reviewed application
            act_pdf = active_req.get("pdf_path")
            if not act_pdf or not os.path.exists(act_pdf):
                act_pdf = generate_requisition_pdf(active_req)
                database.update_requisition_pdf(active_req["requisition_no"], os.path.basename(act_pdf), act_pdf)

            if os.path.exists(act_pdf):
                with open(act_pdf, "rb") as f:
                    act_pdf_bytes = f.read()
                st.download_button(
                    label=f"📄 Download Requisition PDF ({active_req['requisition_no']})",
                    data=act_pdf_bytes,
                    file_name=f"Requisition_{active_req['roll_number']}_{active_req['student_name']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    # Export registry to CSV
    st.markdown("---")
    full_df = database.export_to_dataframe()
    csv_payload = full_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Full Registry to CSV",
        data=csv_payload,
        file_name=f"requisitions_master_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


# =============================================================================
# TAB 4: GUIDELINES & POLICY
# =============================================================================
with tab_policy:
    st.markdown("### 📋 Institutional Requisition Guidelines & Policies")
    st.caption("Official regulations governing student certificates, bonafide requests, and institutional endorsements.")

    st.markdown(f"""
    <div class="section-card">
        <h4 style="margin-top: 0; color: #38bdf8;">⏱️ Standard Processing Protocol</h4>
        <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1;">
            {PROCESSING_TIME_TEXT}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📑 Required Enclosures Checklist")
    guidelines_table = pd.DataFrame([
        {"Requisition Category": "Bonafide Certificate", "Applicable Purpose": "Passport, Bank Account, Education Loan, Concession", "Required Enclosures": "College ID Card, Current Year Fee Receipt"},
        {"Requisition Category": "Student Certificate", "Applicable Purpose": "Visa, Embassy Verification, Official Endorsements", "Required Enclosures": "Previous Year Marksheet, Identity Card"},
        {"Requisition Category": "Scholarship", "Applicable Purpose": "NSP, State MahaDBT, Corporate CSR Schemes", "Required Enclosures": "Income Certificate, Marksheet, Fee Receipt"},
        {"Requisition Category": "NOC (No Objection)", "Applicable Purpose": "Hackathons, External Competitions, Project Visits", "Required Enclosures": "Event Invitation / Brochure, Team Details"},
        {"Requisition Category": "Academic Permission", "Applicable Purpose": "Attendance Condonation, Medical Leave, Lab Access", "Required Enclosures": "Medical Fitness Certificate / Parent Letter"},
        {"Requisition Category": "Examination", "Applicable Purpose": "Revaluation, Duplicate Hall Ticket, Grade Card", "Required Enclosures": "Hall Ticket copy, Exam Fee Receipt"},
        {"Requisition Category": "Internship NOC", "Applicable Purpose": "Semester Internship, Industrial Summer Training", "Required Enclosures": "Company Offer Letter with Duration & Stipend"},
        {"Requisition Category": "Placement", "Applicable Purpose": "Pre-Placement Talks, Off-Campus Verification", "Required Enclosures": "T&P Cell Verification Slip"}
    ])
    st.dataframe(guidelines_table, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-card">
        <h4 style="margin-top: 0; color: #38bdf8;">🔄 Requisition Workflow Hierarchy</h4>
        <ol style="font-size: 14px; line-height: 1.8; color: #cbd5e1; margin-bottom: 0;">
            <li><strong>Digital Submission:</strong> Student submits the form with mandatory fields and declaration.</li>
            <li><strong>Departmental Scrutiny:</strong> Faculty advisor / Academic coordinator verifies roll number and documents.</li>
            <li><strong>HoD Endorsement:</strong> Head of Department reviews the request and adds institutional remarks.</li>
            <li><strong>Forwarding Routing:</strong> Request routed to Vice Principal, Exam Cell, Scholarship Cell, or Accounts.</li>
            <li><strong>Final Approval:</strong> Principal / Vice Principal issues official sanction and digital PDF is signed.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
