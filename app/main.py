import streamlit as st
import pandas as pd
import numpy as np
import datetime
from config import APP_TITLE, validate_config
from components.floating_chat import render_floating_chat
from utils.theme import inject_theme

def setup_page():
    """Configures the main Streamlit page settings."""
    st.set_page_config(
        page_title="Cityfront Clinical Hub",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def seed_session_state():
    """Seeds sample data into session state for high-fidelity interactive prototyping."""
    if "scheduled_appointments" not in st.session_state:
        st.session_state.scheduled_appointments = [
            {"patient": "Alice Sterling", "doctor": "Emily Chen, MD (Cardiology)", "date": "2026-06-01", "time": "09:00 AM", "symptoms": "Mild palpitations"},
            {"patient": "Robert Miller", "doctor": "Sarah Jenkins, MD (Neurology)", "date": "2026-06-02", "time": "11:30 AM", "symptoms": "Tension headaches"},
            {"patient": "John Doe", "doctor": "Marcus Vance, MD (Orthopedics)", "date": "2026-06-03", "time": "02:00 PM", "symptoms": "Severe lower back pain"}
        ]

def render_landing_page():
    """Renders the high-fidelity hospital clinical portal."""
    
    # 1. Inject the premium clinical design system
    inject_theme()
    
    # 2. Seed mock records
    seed_session_state()
    
    # 3. Render Custom Hospital Navbar Header
    st.markdown(
        """
        <div class="hospital-header">
            <div>
                <h1>🏥 Cityfront Clinical Hub</h1>
                <p>Integrated AI Agentic Platform &amp; Healthcare SaaS</p>
            </div>
            <div class="header-badge">
                <span class="live-dot"></span>Active Insurance Connectors: 14
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 4. Render Layout Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Clinical Dashboard", 
        "📅 Appointment Booking", 
        "👥 Specialist Profiles", 
        "📁 Patient Records", 
        "💳 Billing & Payments"
    ])
    
    # ==================== TAB 1: CLINICAL DASHBOARD ====================
    with tab1:
        st.markdown("<h2 class='clinical-title'>🏥 Clinical Operations & Analytics</h2>", unsafe_allow_html=True)
        st.markdown("<p class='clinical-subtitle'>Real-time tracking of active clinic metrics, admissions, and pending prior authorization clearances.</p>", unsafe_allow_html=True)
        
        # Statistics Widgets (shades of pastel blue cards)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                """
                <div class="stat-card-blue">
                    <div class="stat-label">Patients Admitted</div>
                    <div class="stat-value">1,482</div>
                    <div class="stat-delta" style="color:var(--badge-green-text);">📈 +4.2% from yesterday</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                """
                <div class="stat-card-blue">
                    <div class="stat-label">Specialists Online</div>
                    <div class="stat-value">18</div>
                    <div class="stat-delta">🕒 4 on active call shifts</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                """
                <div class="stat-card-blue">
                    <div class="stat-label">Pending Authorizations</div>
                    <div class="stat-value" style="color:var(--badge-red-text);">7 Cases</div>
                    <div class="stat-delta" style="color:var(--badge-red-text);">⚠️ Urgent review required</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c4:
            st.markdown(
                """
                <div class="stat-card-blue">
                    <div class="stat-label">Claims Cleared Rate</div>
                    <div class="stat-value">94.2%</div>
                    <div class="stat-delta" style="color:var(--badge-green-text);">🎯 Exceeds national baseline</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        st.divider()
        
        # Grid layout for Analytics Chart and Pending Tasks
        cg1, cg2 = st.columns([2, 1])
        
        with cg1:
            st.markdown(
                """
                <div class="hospital-card" style="height: 100%;">
                    <h3 style="margin-top:0; color:var(--text-accent); font-family:'Outfit',sans-serif;">📊 Monthly Patient Admissions &amp; Policy Clearance</h3>
                    <p style="font-size:12px; color:var(--text-secondary); margin-top:-8px;">Correlating inbound clinical cases against autonomous AI agent processing approvals.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Draw Area Chart inside card
            chart_data = pd.DataFrame(
                np.random.randint(45, 120, size=(12, 2)),
                columns=['Admissions', 'AI Authorizations Approved'],
                index=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            )
            st.area_chart(chart_data, height=220, color=["#3b82f6", "#93c5fd"])
            
        with cg2:
            st.markdown(
                """
                <div class="hospital-card">
                    <h3 style="margin-top:0; color:var(--text-accent); font-family:'Outfit',sans-serif;">⚡ Quick Actions</h3>
                    <p style="font-size:12px; color:var(--text-secondary); margin-top:-8px;">Launch active clinical agents and support loops.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("#### 📋 Prior Auth Assistant")
            st.markdown("Run autonomous Multi-Agent loop to extract charts and verify insurance rules.")
            if st.button("🚀 Enter Prior Authorization Workspace", type="primary", use_container_width=True):
                st.switch_page("pages/2_📋_Prior_Authorization.py")
                
            st.divider()
            
            st.markdown("#### 💬 Conversational Support")
            st.markdown("Consult general clinical guidelines or review EHR memories.")
            if st.button("💬 Launch Conversational Chat", use_container_width=True):
                st.switch_page("pages/1_💬_Chat_Assistant.py")
                
        st.divider()
        
        # Recent Admissions Logs Data Grid
        st.markdown("<h3 class='clinical-title' style='font-size:18px; margin-bottom:6px;'>📋 Recent Admissions Ledger</h3>", unsafe_allow_html=True)
        
        logs_table = """
        <table class="clinical-table">
            <thead>
                <tr>
                    <th>Patient Name</th>
                    <th>DOB</th>
                    <th>Consulting Specialist</th>
                    <th>Diagnosis / ICD-10</th>
                    <th>Insurance Carrier</th>
                    <th>Prior Auth Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>John Doe</td>
                    <td>1984-11-12</td>
                    <td>Emily Chen, MD</td>
                    <td>Lumbar radiculopathy (M54.16)</td>
                    <td>Cityfront PPO</td>
                    <td><span class="badge badge-orange">⚠️ Pending Review</span></td>
                </tr>
                <tr>
                    <td>Jane Smith</td>
                    <td>1991-05-24</td>
                    <td>Sarah Jenkins, MD</td>
                    <td>Severe Migraine (G43.909)</td>
                    <td>Medicaid Select</td>
                    <td><span class="badge badge-green">✅ Cleared</span></td>
                </tr>
                <tr>
                    <td>Arthur Pendelton</td>
                    <td>1958-08-30</td>
                    <td>Marcus Vance, MD</td>
                    <td>Osteoarthritis of Knee (M17.11)</td>
                    <td>Medicare Advantage</td>
                    <td><span class="badge badge-green">✅ Cleared</span></td>
                </tr>
                <tr>
                    <td>Clarissa Harlowe</td>
                    <td>1973-12-05</td>
                    <td>Robert Carter, MD</td>
                    <td>Acute Bronchitis (J20.9)</td>
                    <td>Blue Cross Blue Shield</td>
                    <td><span class="badge badge-gray">📝 Exempt</span></td>
                </tr>
            </tbody>
        </table>
        """
        st.markdown(logs_table, unsafe_allow_html=True)
        
    # ==================== TAB 2: APPOINTMENT BOOKING ====================
    with tab2:
        st.markdown("<h2 class='clinical-title'>📅 Interactive Appointment Scheduler</h2>", unsafe_allow_html=True)
        st.markdown("<p class='clinical-subtitle'>Schedule consultations, configure diagnostic slots, and manage specialist availability calendars.</p>", unsafe_allow_html=True)
        
        ca1, ca2 = st.columns([1, 1])
        
        with ca1:
            st.markdown(
                """
                <div class="hospital-card">
                    <h3 style="margin-top:0; color:var(--text-accent); font-family:'Outfit',sans-serif;">✍️ Patient Intake &amp; Slot Booking</h3>
                    <p style="font-size:12px; color:var(--text-secondary); margin-top:-8px;">Select from active on-duty specialists and reserve clinical slots.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with st.form("appointment_booking_form"):
                p_name = st.text_input("Patient Full Name", placeholder="e.g. Johnathan Doe")
                doc_select = st.selectbox(
                    "Select Medical Specialist & Department",
                    options=[
                        "Emily Chen, MD (Cardiology)",
                        "Sarah Jenkins, MD (Neurology)",
                        "Marcus Vance, MD (Orthopedics)",
                        "Robert Carter, MD (Pediatrics)"
                    ]
                )
                
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    appt_date = st.date_input("Appointment Date", value=datetime.date.today() + datetime.timedelta(days=1))
                with c_col2:
                    appt_time = st.selectbox("Preferred Time Slot", ["09:00 AM", "10:00 AM", "11:00 AM", "11:30 AM", "02:00 PM", "03:00 PM", "04:30 PM"])
                    
                symptoms_text = st.text_area("Chief Complaint / Clinical Symptoms", placeholder="Describe primary symptoms...")
                
                submit_booking = st.form_submit_button("📅 Finalize Clinical Appointment", type="primary")
                
                if submit_booking:
                    if p_name:
                        st.session_state.scheduled_appointments.append({
                            "patient": p_name,
                            "doctor": doc_select,
                            "date": str(appt_date),
                            "time": appt_time,
                            "symptoms": symptoms_text if symptoms_text else "General wellness checkup"
                        })
                        st.success(f"🎉 Appointment for **{p_name}** with **{doc_select}** successfully scheduled!")
                        time_delay = 0.5
                        import time
                        time.sleep(time_delay)
                        st.rerun()
                    else:
                        st.error("Please provide the patient name to finalize the scheduling.")
                        
        with ca2:
            st.markdown(
                """
                <div class="hospital-card">
                    <h3 style="margin-top:0; color:var(--text-accent); font-family:'Outfit',sans-serif;">📅 Active Booking Registry</h3>
                    <p style="font-size:12px; color:var(--text-secondary); margin-top:-8px;">Live registry of reserved slots and scheduled patient intake pipelines.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            for idx, appt in enumerate(st.session_state.scheduled_appointments):
                st.markdown(
                    f"""
                    <div style="background-color:var(--bg-surface); border:1px solid var(--border-default); border-left:4px solid var(--blue-500); border-radius:10px; padding:15px; margin-bottom:12px; box-shadow:var(--shadow-sm); transition:box-shadow 0.2s ease;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="color:var(--text-primary); font-size:15px;">👤 {appt['patient']}</strong>
                            <span style="font-size:12px; font-weight:600; color:var(--blue-600); background:var(--blue-50); padding:3px 10px; border-radius:12px; border:1px solid var(--blue-200);">{appt['time']}</span>
                        </div>
                        <div style="font-size:13px; color:var(--text-secondary); margin-top:6px;">🩺 <strong>Specialist</strong>: {appt['doctor']}</div>
                        <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">📅 <strong>Date</strong>: {appt['date']} &nbsp;|&nbsp; 📝 <strong>Symptoms</strong>: {appt['symptoms']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
    # ==================== TAB 3: SPECIALIST PROFILES ====================
    with tab3:
        st.markdown("<h2 class='clinical-title'>👥 Clinic Specialist Roster</h2>", unsafe_allow_html=True)
        st.markdown("<p class='clinical-subtitle'>Browse active specialists, check board certifications, ratings, and live clinic call status.</p>", unsafe_allow_html=True)
        
        # Grid of doctor specialists
        cd1, cd2 = st.columns(2)
        
        with cd1:
            st.markdown(
                """
                <div class="doc-profile-card">
                    <div style="font-size:38px; background:var(--blue-50); width:68px; height:68px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2px solid var(--blue-200); flex-shrink:0;">👩‍⚕️</div>
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                            <h4 style="margin:0; color:var(--text-primary); font-family:'Outfit',sans-serif; font-weight:700;">Emily Chen, MD</h4>
                            <span class="badge badge-green">🟢 Available</span>
                        </div>
                        <div style="font-size:13px; color:var(--text-accent); font-weight:600; margin-top:3px;">Chief of Interventional Cardiology</div>
                        <div style="font-size:12px; color:var(--text-secondary); margin-top:5px;">⭐ <strong>4.9</strong> (284 reviews) &nbsp;·&nbsp; 💼 14 Yrs Exp</div>
                        <div style="font-size:11px; color:var(--text-muted); margin-top:3px;">NPI: 1982730492 &nbsp;·&nbsp; Board Certified</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="doc-profile-card">
                    <div style="font-size:38px; background:var(--blue-50); width:68px; height:68px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2px solid var(--blue-200); flex-shrink:0;">👨‍⚕️</div>
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                            <h4 style="margin:0; color:var(--text-primary); font-family:'Outfit',sans-serif; font-weight:700;">Marcus Vance, MD</h4>
                            <span class="badge badge-orange">🟠 In Surgery</span>
                        </div>
                        <div style="font-size:13px; color:var(--text-accent); font-weight:600; margin-top:3px;">Orthopedics &amp; Joint Reconstruction</div>
                        <div style="font-size:12px; color:var(--text-secondary); margin-top:5px;">⭐ <strong>4.7</strong> (192 reviews) &nbsp;·&nbsp; 💼 18 Yrs Exp</div>
                        <div style="font-size:11px; color:var(--text-muted); margin-top:3px;">NPI: 1472850392 &nbsp;·&nbsp; Board Certified</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with cd2:
            st.markdown(
                """
                <div class="doc-profile-card">
                    <div style="font-size:38px; background:var(--blue-50); width:68px; height:68px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2px solid var(--blue-200); flex-shrink:0;">👩‍⚕️</div>
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                            <h4 style="margin:0; color:var(--text-primary); font-family:'Outfit',sans-serif; font-weight:700;">Sarah Jenkins, MD</h4>
                            <span class="badge badge-green">🟢 Available</span>
                        </div>
                        <div style="font-size:13px; color:var(--text-accent); font-weight:600; margin-top:3px;">Director of Clinical Neurology</div>
                        <div style="font-size:12px; color:var(--text-secondary); margin-top:5px;">⭐ <strong>4.8</strong> (314 reviews) &nbsp;·&nbsp; 💼 11 Yrs Exp</div>
                        <div style="font-size:11px; color:var(--text-muted); margin-top:3px;">NPI: 1102947265 &nbsp;·&nbsp; Board Certified</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="doc-profile-card">
                    <div style="font-size:38px; background:var(--blue-50); width:68px; height:68px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2px solid var(--blue-200); flex-shrink:0;">👨‍⚕️</div>
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                            <h4 style="margin:0; color:var(--text-primary); font-family:'Outfit',sans-serif; font-weight:700;">Robert K. Carter, MD</h4>
                            <span class="badge badge-green">🟢 Available</span>
                        </div>
                        <div style="font-size:13px; color:var(--text-accent); font-weight:600; margin-top:3px;">Pediatrics &amp; Neonatal Care</div>
                        <div style="font-size:12px; color:var(--text-secondary); margin-top:5px;">⭐ <strong>4.9</strong> (412 reviews) &nbsp;·&nbsp; 💼 9 Yrs Exp</div>
                        <div style="font-size:11px; color:var(--text-muted); margin-top:3px;">NPI: 1048265839 &nbsp;·&nbsp; Board Certified</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    # ==================== TAB 4: PATIENT RECORDS ====================
    with tab4:
        st.markdown("<h2 class='clinical-title'>📁 Electronic Health Records (EHR)</h2>", unsafe_allow_html=True)
        st.markdown("<p class='clinical-subtitle'>Securely view electronic chart notes, check diagnoses, and verify prior authorization necessity matching.</p>", unsafe_allow_html=True)
        
        # Search Box
        st.text_input("🔍 Filter EHR Patient Directory", placeholder="Type patient name, DOB, or NPI...", key="ehr_filter_search")
        
        patient_records_table = """
        <table class="clinical-table">
            <thead>
                <tr>
                    <th>Patient ID</th>
                    <th>Patient Name</th>
                    <th>Age/Gender</th>
                    <th>Active Diagnosis</th>
                    <th>Last Visit Date</th>
                    <th>Assigned Physician</th>
                    <th>EHR Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>#CF-88273</strong></td>
                    <td>John Doe</td>
                    <td>41 / Male</td>
                    <td>Lumbar disc herniation with radiculopathy</td>
                    <td>2026-05-27</td>
                    <td>Emily Chen, MD</td>
                    <td><span style="color:var(--text-accent); font-weight:600; cursor:pointer;">📁 View Chart</span> | <span style="color:var(--text-accent); font-weight:600; cursor:pointer;">📋 Draft Prior Auth</span></td>
                </tr>
                <tr>
                    <td><strong>#CF-99482</strong></td>
                    <td>Jane Smith</td>
                    <td>35 / Female</td>
                    <td>Chronic migraine without aura</td>
                    <td>2026-05-20</td>
                    <td>Sarah Jenkins, MD</td>
                    <td><span style="color:var(--text-accent); font-weight:600; cursor:pointer;">📁 View Chart</span></td>
                </tr>
                <tr>
                    <td><strong>#CF-10482</strong></td>
                    <td>Clarissa Harlowe</td>
                    <td>52 / Female</td>
                    <td>Acute bronchitis, unspecified</td>
                    <td>2026-05-15</td>
                    <td>Robert Carter, MD</td>
                    <td><span style="color:var(--text-accent); font-weight:600; cursor:pointer;">📁 View Chart</span></td>
                </tr>
                <tr>
                    <td><strong>#CF-77492</strong></td>
                    <td>Robert Miller</td>
                    <td>68 / Male</td>
                    <td>Osteoarthritis of the right knee</td>
                    <td>2026-05-10</td>
                    <td>Marcus Vance, MD</td>
                    <td><span style="color:var(--text-accent); font-weight:600; cursor:pointer;">📁 View Chart</span> | <span style="color:var(--text-accent); font-weight:600; cursor:pointer;">📋 Draft Prior Auth</span></td>
                </tr>
            </tbody>
        </table>
        """
        st.markdown(patient_records_table, unsafe_allow_html=True)
        
    # ==================== TAB 5: BILLING & PAYMENTS ====================
    with tab5:
        st.markdown("<h2 class='clinical-title'>💳 Billing, Payment Ledger & Claims</h2>", unsafe_allow_html=True)
        st.markdown("<p class='clinical-subtitle'>Review medical billing codes, check outstanding balance pipelines, and track payer reimbursement distributions.</p>", unsafe_allow_html=True)
        
        cb1, cb2 = st.columns([1, 1.5])
        
        with cb1:
            st.markdown(
                """
                <div class="hospital-card">
                    <h3 style="margin-top:0; color:var(--text-accent); font-family:'Outfit',sans-serif;">💰 Revenue Cycle Summary</h3>
                    <p style="font-size:12px; color:var(--text-secondary); margin-top:-8px;">Platform billing efficiency and cleared claims tracking.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                """
                <div style="background:var(--blue-50); border:1px solid var(--blue-200); border-radius:10px; padding:18px; margin-bottom:12px;">
                    <div style="font-size:11px; font-weight:700; color:var(--blue-700); letter-spacing:0.6px; text-transform:uppercase;">Total Outstanding Claims</div>
                    <div style="font-size:28px; font-weight:800; color:var(--text-primary); margin-top:4px; font-family:'Outfit',sans-serif;">$48,920.00</div>
                </div>
                <div style="background:var(--success-bg); border:1px solid var(--success-border); border-radius:10px; padding:18px; margin-bottom:12px;">
                    <div style="font-size:11px; font-weight:700; color:var(--success-text); letter-spacing:0.6px; text-transform:uppercase;">Reimbursement Collected (YTD)</div>
                    <div style="font-size:28px; font-weight:800; color:var(--success-text); margin-top:4px; font-family:'Outfit',sans-serif;">$1,248,300.00</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with cb2:
            st.markdown(
                """
                <div class="hospital-card">
                    <h3 style="margin-top:0; color:var(--text-accent); font-family:'Outfit',sans-serif;">💸 Recent Transaction Ledger</h3>
                    <p style="font-size:12px; color:var(--text-secondary); margin-top:-8px;">Payer billing clearance log and individual code breakdowns.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            billing_table = """
            <table class="clinical-table">
                <thead>
                    <tr>
                        <th>Invoice ID</th>
                        <th>Patient Name</th>
                        <th>CPT Code</th>
                        <th>Insurance Carrier</th>
                        <th>Charge</th>
                        <th>Claim Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>#INV-2048</strong></td>
                        <td>John Doe</td>
                        <td>72148 (Lumbar MRI)</td>
                        <td>Cityfront PPO</td>
                        <td>$1,200.00</td>
                        <td><span class="badge badge-orange">⚠️ Under Claim Audit</span></td>
                    </tr>
                    <tr>
                        <td><strong>#INV-2049</strong></td>
                        <td>Jane Smith</td>
                        <td>99214 (Outpatient Visit)</td>
                        <td>Medicaid Select</td>
                        <td>$185.00</td>
                        <td><span class="badge badge-green">✅ Reimbursed</span></td>
                    </tr>
                    <tr>
                        <td><strong>#INV-2050</strong></td>
                        <td>Arthur Pendelton</td>
                        <td>27447 (Knee Replacement)</td>
                        <td>Medicare Advantage</td>
                        <td>$14,500.00</td>
                        <td><span class="badge badge-green">✅ Reimbursed</span></td>
                    </tr>
                </tbody>
            </table>
            """
            st.markdown(billing_table, unsafe_allow_html=True)
            
    # 5. Render Floating Chat Widget
    render_floating_chat()

if __name__ == "__main__":
    setup_page()
    render_landing_page()