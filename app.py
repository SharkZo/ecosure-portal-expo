import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import sqlite3
import pandas as pd
import re
import time
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image
import os
from datetime import datetime

# ==========================================
# PAGE CONFIG (Must be first Streamlit command)
# ==========================================
logo_path = "Ecosurelogo.jpg"
logo = None
if os.path.exists(logo_path):
    logo = Image.open(logo_path)

st.set_page_config(
    page_title="ECOSURE Portal",
    page_icon=logo if logo else "🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ENHANCED CSS STYLING
# ==========================================
st.markdown("""
<style>
    /* Import fonts */
    @import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap)');
    
    /* Hide Streamlit defaults */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fdf8 0%, #e8f5e9 50%, #f1f8e9 100%);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B4332 0%, #2D6A4F 100%);
        border-right: none;
    }
    
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
    }
    
    /* Card components */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 8px 32px rgba(27, 67, 50, 0.08);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(27, 67, 50, 0.12);
    }
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 50%, #40916C 100%);
        border-radius: 24px;
        padding: 40px;
        color: white;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid #e8f5e9;
        box-shadow: 0 4px 20px rgba(27, 67, 50, 0.06);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 30px rgba(27, 67, 50, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1B4332;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 8px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-trend {
        font-size: 0.8rem;
        margin-top: 10px;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }
    
    .trend-up {
        background: #d4edda;
        color: #155724;
    }
    
    .trend-neutral {
        background: #fff3cd;
        color: #856404;
    }
    
    /* Job cards */
    .job-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 2px solid transparent;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 12px;
    }
    
    .job-card:hover {
        border-color: #2D6A4F;
        box-shadow: 0 8px 25px rgba(45, 106, 79, 0.15);
    }
    
    .job-card.selected {
        border-color: #1B4332;
        background: linear-gradient(135deg, #f8fdf8 0%, #e8f5e9 100%);
    }
    
    .job-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1B4332;
        margin-bottom: 4px;
    }
    
    .job-company {
        font-size: 0.85rem;
        color: #666;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .job-badge {
        background: linear-gradient(135deg, #2D6A4F, #40916C);
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Status badges */
    .status-badge {
        padding: 8px 16px;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    .status-accepted {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        color: #155724;
        border: 1px solid #b1dfbb;
    }
    
    .status-rejected {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        color: #721c24;
        border: 1px solid #f1b0b7;
    }
    
    .status-pending {
        background: linear-gradient(135deg, #fff3cd, #ffeeba);
        color: #856404;
        border: 1px solid #ffc107;
    }
    
    /* Auth form styling */
    .auth-container {
        background: white;
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(27, 67, 50, 0.1);
        border: 1px solid #e8f5e9;
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .auth-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1B4332;
        margin-bottom: 8px;
    }
    
    .auth-subtitle {
        color: #666;
        font-size: 0.95rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(27, 67, 50, 0.25);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e8f5e9;
        padding: 12px 16px;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2D6A4F;
        box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.1);
    }
    
    /* File uploader */
    .stFileUploader > div {
        border-radius: 16px;
        border: 2px dashed #2D6A4F;
        background: rgba(45, 106, 79, 0.03);
        padding: 30px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        background: rgba(45, 106, 79, 0.08);
        border-color: #1B4332;
    }
    
    /* Progress indicators */
    .progress-step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 0;
    }
    
    .step-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .step-complete {
        background: #2D6A4F;
        color: white;
    }
    
    .step-active {
        background: #fff3cd;
        color: #856404;
        border: 2px solid #ffc107;
    }
    
    .step-pending {
        background: #f8f9fa;
        color: #adb5bd;
        border: 2px solid #dee2e6;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e8f5e9;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        background: white;
        border: 2px solid #e8f5e9;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
        color: white;
        border-color: transparent;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        font-weight: 600;
        color: #1B4332;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e8f5e9, transparent);
        margin: 30px 0;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2D6A4F;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #1B4332;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# GOOGLE API SETUP
# ==========================================
def setup_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return True
    except Exception:
        pass
    
    with st.sidebar.expander("🔐 API Configuration", expanded=False):
        api_key_input = st.text_input(
            "Gemini API Key:",
            type="password",
            help="Required for AI-powered CV analysis"
        )
        if api_key_input:
            genai.configure(api_key=api_key_input)
            return True
    return False

api_ready = setup_gemini()

# ==========================================
# DATABASE LOGIC
# ==========================================
def init_db():
    conn = sqlite3.connect('ecosure.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  fullname TEXT, email TEXT UNIQUE, password TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  candidate_email TEXT, job_title TEXT, score_val INTEGER,
                  report TEXT, status TEXT DEFAULT 'Pending',
                  cv_blob BLOB,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

init_db()

# ==========================================
# AI & PDF LOGIC
# ==========================================
def get_gemini_response(prompt):
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Evaluation Error: {str(e)}"

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += str(extracted)
    return text

def send_email(target_email, candidate_name, score, feedback):
    try:
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASS"]
        
        msg = MIMEMultipart()
        msg['From'] = f"ECOSURE Recruitment <{sender_email}>"
        msg['To'] = target_email
        msg['Subject'] = "🎉 Congratulations! You've Been Accepted - ECOSURE"
        
        body = f"""Dear Candidate,

Congratulations! 🎉

We are thrilled to inform you that after careful review, you have been ACCEPTED for the position at ECOSURE Portal.

Your AI Match Score: {score}/100

What's Next?
Our HR Team will contact you within 2-3 business days regarding:
• Onboarding documentation
• Interview scheduling
• Role-specific requirements

Please ensure your contact information is current and monitor your inbox.

Welcome to the ECOSURE family!

Best Regards,
ECOSURE Recruitment Team
🌿 Sustainable Careers for a Greener Future"""

        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# ==========================================
# JOB DATABASE
# ==========================================
jobs_db = {
    "Senior Python Developer": {
        "company": "ECOSURE Tech",
        "location": "Remote / Jakarta",
        "type": "Full-time",
        "salary": "$80K - $120K",
        "req": "• 5+ years Python experience\n• Django/FastAPI expertise\n• Docker & Kubernetes\n• CI/CD pipelines",
        "icon": "💻"
    },
    "AI & ML Engineer": {
        "company": "ECOSURE Intelligence",
        "location": "Singapore",
        "type": "Full-time",
        "salary": "$100K - $150K",
        "req": "• Deep Learning specialist\n• LLM production experience\n• PyTorch/TensorFlow\n• MLOps knowledge",
        "icon": "🤖"
    },
    "UI/UX Designer": {
        "company": "ECOSURE Creative",
        "location": "Remote",
        "type": "Contract",
        "salary": "$60K - $90K",
        "req": "• Figma/Adobe XD portfolio\n• Sustainable design principles\n• WCAG accessibility\n• User research",
        "icon": "🎨"
    },
    "Data Scientist": {
        "company": "ECOSURE Analytics",
        "location": "Hybrid - Jakarta",
        "type": "Full-time",
        "salary": "$70K - $110K",
        "req": "• SQL & Python expert\n• Predictive modeling\n• Environmental data analysis\n• Visualization skills",
        "icon": "📊"
    }
}

# ==========================================
# SESSION STATE
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'hr_logged_in' not in st.session_state:
    st.session_state['hr_logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""
if 'selected_job' not in st.session_state:
    st.session_state['selected_job'] = list(jobs_db.keys())[0]

# ==========================================
# SIDEBAR
# ==========================================
if logo:
    st.sidebar.image(logo, use_container_width=True)

st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <h2 style="color: white; font-size: 1.4rem; margin: 0; font-weight: 700;">ECOSURE</h2>
        <p style="color: rgba(255,255,255,0.7); font-size: 0.8rem; margin: 5px 0 0 0;">Sustainable Recruitment</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

user_role = st.sidebar.selectbox(
    "🚪 Portal Access",
    ["Applicant Portal", "HR Management"],
    label_visibility="collapsed"
)

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="padding: 15px; background: rgba(255,255,255,0.05); border-radius: 12px; margin-top: 20px;">
        <p style="color: rgba(255,255,255,0.9); font-size: 0.75rem; margin: 0 0 8px 0; font-weight: 600;">⚡ System Status</p>
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: rgba(255,255,255,0.6); font-size: 0.7rem;">AI Engine</span>
            <span style="color: #90EE90; font-size: 0.7rem;">● Online</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: rgba(255,255,255,0.6); font-size: 0.7rem;">Response Time</span>
            <span style="color: rgba(255,255,255,0.8); font-size: 0.7rem;">~240ms</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# APPLICANT PORTAL
# ==========================================
if user_role == "Applicant Portal":
    
    if not st.session_state['logged_in']:
        # Login/Register Page
        col_spacer1, col_auth, col_spacer2 = st.columns([1, 2, 1])
        
        with col_auth:
            st.markdown("""
                <div class="auth-container">
                    <div class="auth-header">
                        <div style="font-size: 3rem; margin-bottom: 15px;">🌿</div>
                        <h1 class="auth-title">Welcome to ECOSURE</h1>
                        <p class="auth-subtitle">Your gateway to sustainable careers</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            auth_mode = st.radio(
                "Choose action:",
                ["Sign In", "Create Account"],
                horizontal=True,
                label_visibility="collapsed"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if auth_mode == "Sign In":
                email = st.text_input("📧 Email Address", placeholder="Enter your email")
                password = st.text_input("🔒 Password", type='password', placeholder="Enter your password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Sign In →", use_container_width=True):
                    if email and password:
                        conn = sqlite3.connect('ecosure.db')
                        c = conn.cursor()
                        c.execute('SELECT password FROM users WHERE email = ?', (email,))
                        data = c.fetchone()
                        conn.close()
                        
                        if data and check_hashes(password, data[0]):
                            st.session_state['logged_in'] = True
                            st.session_state['user_email'] = email
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please try again.")
                    else:
                        st.warning("Please fill in all fields.")
            else:
                new_user = st.text_input("👤 Full Name", placeholder="Enter your full name")
                new_email = st.text_input("📧 Email Address", placeholder="Enter your email")
                new_password = st.text_input("🔒 Password", type='password', placeholder="Create a password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Create Account →", use_container_width=True):
                    if new_user and new_email and new_password:
                        conn = sqlite3.connect('ecosure.db')
                        c = conn.cursor()
                        try:
                            c.execute(
                                'INSERT INTO users(fullname, email, password) VALUES (?,?,?)',
                                (new_user, new_email, make_hashes(new_password))
                            )
                            conn.commit()
                            st.success("✅ Account created successfully! Please sign in.")
                        except sqlite3.IntegrityError:
                            st.error("❌ Email already registered.")
                        conn.close()
                    else:
                        st.warning("Please fill in all fields.")
            
            st.markdown("""
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e8f5e9;">
                    <p style="color: #888; font-size: 0.8rem;">
                        🔒 Your data is encrypted and secure
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    else:
        # Logged in - Main Application
        
        # Top bar with user info
        col_welcome, col_signout = st.columns([4, 1])
        with col_welcome:
            st.markdown(f"""
                <p style="color: #666; font-size: 0.9rem; margin: 0;">
                    Welcome back, <strong style="color: #1B4332;">{st.session_state['user_email']}</strong>
                </p>
            """, unsafe_allow_html=True)
        with col_signout:
            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state['logged_in'] = False
                st.session_state['user_email'] = ""
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation
        nav_choice = st.radio(
            "Navigate:",
            ["🚀 Job Board", "📋 My Applications"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if nav_choice == "🚀 Job Board":
            # Hero Section
            st.markdown("""
                <div class="hero-section">
                    <h1 class="hero-title">Find Your Dream Role 🌍</h1>
                    <p class="hero-subtitle">Join our mission to build sustainable technology for a greener future</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Job listing layout
            col_jobs, col_details = st.columns([1, 2])
            
            with col_jobs:
                st.markdown("### Open Positions")
                
                for job_name, job_info in jobs_db.items():
                    is_selected = st.session_state['selected_job'] == job_name
                    
                    if st.button(
                        f"{job_info['icon']} {job_name}\n{job_info['company']}",
                        key=f"job_{job_name}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state['selected_job'] = job_name
                        st.rerun()
            
            with col_details:
                job = jobs_db[st.session_state['selected_job']]
                
                st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                            <div>
                                <h2 style="color: #1B4332; margin: 0 0 5px 0; font-size: 1.6rem;">{job['icon']} {st.session_state['selected_job']}</h2>
                                <p style="color: #666; margin: 0;">{job['company']}</p>
                            </div>
                            <span class="job-badge">HIRING</span>
                        </div>
                        
                        <div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <span>📍</span>
                                <span style="color: #666; font-size: 0.9rem;">{job['location']}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <span>💼</span>
                                <span style="color: #666; font-size: 0.9rem;">{job['type']}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <span>💰</span>
                                <span style="color: #666; font-size: 0.9rem;">{job['salary']}</span>
                            </div>
                        </div>
                        
                        <h4 style="color: #1B4332; margin-bottom: 10px;">Requirements</h4>
                        <p style="color: #444; line-height: 1.8; white-space: pre-line;">{job['req']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Application form
                st.markdown("### Submit Your Application")
                
                uploaded_file = st.file_uploader(
                    "Upload your resume (PDF)",
                    type=["pdf"],
                    help="Maximum file size: 10MB"
                )
                
                if st.button("🚀 Submit Application", use_container_width=True, type="primary"):
                    if uploaded_file:
                        if not api_ready:
                            st.error("⚠️ Please configure your API key in the sidebar first.")
                        else:
                            with st.status("🔄 Processing your application...", expanded=True) as status:
                                st.write("📄 Extracting resume content...")
                                time.sleep(0.5)
                                
                                binary_cv = uploaded_file.getvalue()
                                text = input_pdf_text(uploaded_file)
                                
                                st.write("🤖 AI analyzing your profile...")
                                
                                prompt = f"""Analyze this CV for the position of {st.session_state['selected_job']}.
                                
Requirements:
{job['req']}

CV Content:
{text}

Provide:
1. A match score from 0-100
2. Key strengths (3-5 points)
3. Areas for improvement (2-3 points)
4. Overall recommendation

Format your response clearly with headers."""
                                
                                response = get_gemini_response(prompt)
                                
                                # Extract score
                                score_match = re.search(r"(\d+)", response)
                                score = int(score_match.group(1)) if score_match else 50
                                score = min(max(score, 0), 100)  # Clamp between 0-100
                                
                                st.write("💾 Saving your application...")
                                
                                conn = sqlite3.connect('ecosure.db')
                                conn.execute(
                                    "INSERT INTO analysis_results (candidate_email, job_title, score_val, report, cv_blob) VALUES (?,?,?,?,?)",
                                    (st.session_state['user_email'], st.session_state['selected_job'], score, response, binary_cv)
                                )
                                conn.commit()
                                conn.close()
                                
                                status.update(label="✅ Application submitted successfully!", state="complete")
                            
                            st.balloons()
                            
                            # Show results
                            st.markdown(f"""
                                <div class="glass-card" style="border-left: 4px solid #2D6A4F;">
                                    <h3 style="color: #1B4332; margin-bottom: 15px;">📊 AI Analysis Results</h3>
                                    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                                        <div style="text-align: center;">
                                            <div class="metric-value">{score}</div>
                                            <div class="metric-label">Match Score</div>
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander("📝 View Full Analysis", expanded=True):
                                st.markdown(response)
                    else:
                        st.warning("⚠️ Please upload your resume first.")
        
        elif nav_choice == "📋 My Applications":
            st.markdown("""
                <div class="hero-section" style="padding: 30px;">
                    <h1 class="hero-title" style="font-size: 2rem;">My Applications 📋</h1>
                    <p class="hero-subtitle">Track the status of your job applications</p>
                </div>
            """, unsafe_allow_html=True)
            
            conn = sqlite3.connect('ecosure.db')
            df_status = pd.read_sql_query(
                "SELECT * FROM analysis_results WHERE candidate_email = ? ORDER BY timestamp DESC",
                conn,
                params=(st.session_state['user_email'],)
            )
            conn.close()
            
            if not df_status.empty:
                for _, row in df_status.iterrows():
                    status_class = {
                        'Accepted': 'status-accepted',
                        'Rejected': 'status-rejected',
                        'Pending': 'status-pending'
                    }.get(row['status'], 'status-pending')
                    
                    status_icon = {
                        'Accepted': '✅',
                        'Rejected': '❌',
                        'Pending': '⏳'
                    }.get(row['status'], '⏳')
                    
                    st.markdown(f"""
                        <div class="glass-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                                <div>
                                    <h3 style="color: #1B4332; margin: 0 0 5px 0;">{row['job_title']}</h3>
                                    <p style="color: #888; font-size: 0.85rem; margin: 0;">
                                        Applied: {row['timestamp'][:10] if row['timestamp'] else 'N/A'}
                                    </p>
                                </div>
                                <div style="display: flex; align-items: center; gap: 20px;">
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.5rem; font-weight: 700; color: #1B4332;">{row['score_val']}</div>
                                        <div style="font-size: 0.7rem; color: #888; text-transform: uppercase;">Score</div>
                                    </div>
                                    <span class="status-badge {status_class}">{status_icon} {row['status']}</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if row['status'] == 'Accepted':
                        st.success("🎉 Congratulations! Check your email for next steps.")
                    elif row['status'] == 'Rejected':
                        st.info("💪 Don't give up! Consider applying for other positions.")
            else:
                st.markdown("""
                    <div class="glass-card" style="text-align: center; padding: 60px;">
                        <div style="font-size: 4rem; margin-bottom: 20px;">📭</div>
                        <h3 style="color: #1B4332; margin-bottom: 10px;">No Applications Yet</h3>
                        <p style="color: #666;">Start your journey by exploring our open positions!</p>
                    </div>
                """, unsafe_allow_html=True)

# ==========================================
# HR MANAGEMENT PORTAL
# ==========================================
elif user_role == "HR Management":
    
    if not st.session_state['hr_logged_in']:
        col_s1, col_hr_auth, col_s2 = st.columns([1, 2, 1])
        
        with col_hr_auth:
            st.markdown("""
                <div class="auth-container">
                    <div class="auth-header">
                        <div style="font-size: 3rem; margin-bottom: 15px;">🔐</div>
                        <h1 class="auth-title">HR Admin Access</h1>
                        <p class="auth-subtitle">Secure portal for recruitment management</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            hr_password = st.text_input("🔑 Admin Password", type="password", placeholder="Enter admin password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Unlock Dashboard →", use_container_width=True):
                if hr_password == "admin123":
                    st.session_state['hr_logged_in'] = True
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
    
    else:
        # HR Dashboard Header
        col_title, col_actions = st.columns([3, 1])
        with col_title:
            st.markdown("""
                <h1 style="color: #1B4332; font-size: 2rem; font-weight: 800; margin: 0;">
                    📊 HR Intelligence Dashboard
                </h1>
                <p style="color: #666; margin: 5px 0 0 0;">Real-time recruitment analytics and candidate management</p>
            """, unsafe_allow_html=True)
        with col_actions:
            col_lock, col_reset = st.columns(2)
            with col_lock:
                if st.button("🔒 Lock", use_container_width=True):
                    st.session_state['hr_logged_in'] = False
                    st.rerun()
            with col_reset:
                if st.button("🗑️ Reset", use_container_width=True):
                    conn = sqlite3.connect('ecosure.db')
                    conn.execute("DELETE FROM analysis_results")
                    conn.commit()
                    conn.close()
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Load data
        conn = sqlite3.connect('ecosure.db')
        df = pd.read_sql_query("SELECT * FROM analysis_results ORDER BY timestamp DESC", conn)
        
        if not df.empty:
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            
            total_apps = len(df)
            accepted = len(df[df['status'] == 'Accepted'])
            pending = len(df[df['status'] == 'Pending'])
            avg_score = round(df['score_val'].mean(), 1)
            
            with m1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{total_apps}</div>
                        <div class="metric-label">Total Applications</div>
                        <span class="metric-trend trend-up">↑ Active</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with m2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #28a745;">{accepted}</div>
                        <div class="metric-label">Accepted</div>
                        <span class="metric-trend trend-up">✓ Confirmed</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with m3:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #ffc107;">{pending}</div>
                        <div class="metric-label">Pending Review</div>
                        <span class="metric-trend trend-neutral">⏳ Waiting</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with m4:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{avg_score}%</div>
                        <div class="metric-label">Avg Match Score</div>
                        <span class="metric-trend trend-up">📊 Quality</span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Charts Row
            col_chart1, col_chart2 = st.columns([2, 1])
            
            color_map = {
                'Accepted': '#28a745',
                'Rejected': '#dc3545',
                'Pending': '#ffc107'
            }
            
            with col_chart1:
                st.markdown("### 📈 Score Distribution by Candidate")
                fig_bar = px.bar(
                    df,
                    x='candidate_email',
                    y='score_val',
                    color='status',
                    color_discrete_map=color_map,
                    labels={'score_val': 'Match Score', 'candidate_email': 'Candidate'},
                    height=350
                )
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_family="Inter",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col_chart2:
                st.markdown("### 📊 Status Overview")
                status_counts = df['status'].value_counts()
                fig_pie = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    color=status_counts.index,
                    color_discrete_map=color_map,
                    hole=0.6,
                    height=350
                )
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_family="Inter",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.1)
                )
                fig_pie.update_traces(textinfo='value+percent')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            
            # Tabs for management
            tab_pending, tab_all, tab_decision = st.tabs(["⏳ Pending Review", "📋 All Applications", "⚖️ Make Decision"])
            
            with tab_pending:
                df_pending = df[df['status'] == 'Pending']
                if not df_pending.empty:
                    st.dataframe(
                        df_pending[['candidate_email', 'job_title', 'score_val', 'timestamp']].rename(columns={
                            'candidate_email': 'Candidate',
                            'job_title': 'Position',
                            'score_val': 'Score',
                            'timestamp': 'Applied'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success("✅ All applications have been reviewed!")
            
            with tab_all:
                # Filter by job
                job_filter = st.selectbox("Filter by Position:", ["All Positions"] + list(df['job_title'].unique()))
                
                df_filtered = df if job_filter == "All Positions" else df[df['job_title'] == job_filter]
                
                st.dataframe(
                    df_filtered[['candidate_email', 'job_title', 'score_val', 'status', 'timestamp']].rename(columns={
                        'candidate_email': 'Candidate',
                        'job_title': 'Position',
                        'score_val': 'Score',
                        'status': 'Status',
                        'timestamp': 'Applied'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            
            with tab_decision:
                st.markdown("### Select Candidate to Review")
                
                df['display_key'] = df['candidate_email'] + " — " + df['job_title']
                selected_candidate = st.selectbox("Choose candidate:", df['display_key'].unique())
                
                if selected_candidate:
                    candidate = df[df['display_key'] == selected_candidate].iloc[0]
                    
                    col_info, col_action = st.columns([2, 1])
                    
                    with col_info:
                        st.markdown(f"""
                            <div class="glass-card">
                                <h3 style="color: #1B4332; margin-bottom: 15px;">Candidate Profile</h3>
                                <p><strong>Email:</strong> {candidate['candidate_email']}</p>
                                <p><strong>Position:</strong> {candidate['job_title']}</p>
                                <p><strong>Score:</strong> {candidate['score_val']}/100</p>
                                <p><strong>Current Status:</strong> {candidate['status']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if candidate['cv_blob']:
                            st.download_button(
                                "📥 Download CV",
                                data=candidate['cv_blob'],
                                file_name=f"CV_{candidate['candidate_email']}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        with st.expander("📝 AI Analysis Report"):
                            st.markdown(candidate['report'])
                    
                    with col_action:
                        st.markdown("""
                            <div class="glass-card">
                                <h3 style="color: #1B4332; margin-bottom: 15px;">⚖️ Decision</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        decision_options = ["Pending", "Accepted", "Rejected"]
                        current_index = decision_options.index(candidate['status']) if candidate['status'] in decision_options else 0
                        
                        new_status = st.radio(
                            "Select verdict:",
                            decision_options,
                            index=current_index
                        )
                        
                        if st.button("✅ Confirm Decision", use_container_width=True, type="primary"):
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE analysis_results SET status = ? WHERE id = ?",
                                (new_status, int(candidate['id']))
                            )
                            conn.commit()
                            
                            if new_status == "Accepted":
                                with st.spinner("📧 Sending acceptance email..."):
                                    email_sent = send_email(
                                        target_email=candidate['candidate_email'],
                                        candidate_name="Candidate",
                                        score=candidate['score_val'],
                                        feedback=candidate['report']
                                    )
                                    if email_sent:
                                        st.success(f"✅ Email sent to {candidate['candidate_email']}")
                                    else:
                                        st.warning("⚠️ Decision saved but email failed to send")
                            
                            st.success(f"✅ Status updated to {new_status}")
                            time.sleep(1)
                            st.rerun()
        
        else:
            st.markdown("""
                <div class="glass-card" style="text-align: center; padding: 80px;">
                    <div style="font-size: 5rem; margin-bottom: 20px;">📭</div>
                    <h2 style="color: #1B4332; margin-bottom: 10px;">No Applications Yet</h2>
                    <p style="color: #666; font-size: 1.1rem;">Applications will appear here once candidates start applying.</p>
                </div>
            """, unsafe_allow_html=True)
        
        conn.close()
