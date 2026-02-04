import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import sqlite3
import pandas as pd
import re
import time
import plotly.express as px
import hashlib


# ==========================================
# 1. GOOGLE API SETUP (Pro Version)
# ==========================================
import streamlit as st
import google.generativeai as genai

# Fungsi untuk inisialisasi API
def setup_gemini():
    # Gunakan try-except agar tidak error jika file secrets tidak ada di laptop
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            return True
    except:
        # Jika di laptop dan file secrets tidak ditemukan, abaikan saja
        pass
    
    # 2. Untuk versi Local (Laptop)
    # Gunakan expander agar rapi di sidebar
    with st.sidebar.expander("🔐 System Settings", expanded=True):
        api_key_input = st.text_input("Gemini API Key:", type="password", help="Masukkan key hanya jika di laptop")
        
    if api_key_input:
        genai.configure(api_key=api_key_input)
        return True
        
    return False

# Jalankan fungsi setup
api_ready = setup_gemini()

if not api_ready:
    st.sidebar.warning("⚠️ API Key belum terpasang.")

# ==========================================
# 2. DATABASE LOGIC
# ==========================================
def init_db():
    conn = sqlite3.connect('ecosure.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  fullname TEXT, email TEXT UNIQUE, password TEXT)''')
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
# 3. AI & PDF LOGIC
# ==========================================
def get_gemini_response(prompt):
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Evaluation: {str(e)}"

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted: text += str(extracted)
    return text

    # --- FUNGSI KIRIM EMAIL ---
def send_email(target_email, candidate_name, score, feedback):
    try:
        # Mengambil data dari Secrets (Streamlit Cloud)
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASS"]
        
        # Pengaturan pesan
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = target_email
        msg['Subject'] = f"Hasil Seleksi Ecosure Portal - {candidate_name}"
        
        body = f"Halo {candidate_name},\n\nTerima kasih telah melamar. Skor CV Anda: {score}/100\n\nEvaluasi:\n{feedback}"
        msg.attach(MIMEText(body, 'plain'))
        
        # Proses pengiriman melalui server Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Gagal kirim email: {e}")
        return False

# ==========================================
# 4. PREMIUM UI DESIGN (CSS)
# ==========================================
st.set_page_config(page_title="ECOSURE Portal", layout="wide")

st.markdown("""
    <style>
    /* Tambahan Baru: Menghilangkan Header & Footer Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;} /* Menghilangkan menu titik tiga */

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background: radial-gradient(circle at top right, #E8F5E9, #F1F8E9, #FFFFFF); }
    
    /* CSS kamu yang lain tetap di sini... */
    </style>
    """, unsafe_allow_html=True)

# DATA JOB BOARD
jobs_db = {
    "Senior Python Developer": {"company": "ECOSURE Tech", "req": "- 5+ years experience\n- Django/FastAPI Expert\n- Docker & K8s"},
    "AI & ML Engineer": {"company": "ECOSURE Intelligence", "req": "- Deep Learning Specialist\n- LLM Production Experience\n- PyTorch/TensorFlow"},
    "UI/UX Designer": {"company": "ECOSURE Creative", "req": "- Figma/Adobe XD Portfolio\n- Low-Carbon Web Design\n- WCAG Accessibility"},
    "Data Scientist": {"company": "ECOSURE Analytics", "req": "- SQL & Python Expert\n- Predictive Modeling\n- Environmental Data Insight"}
}

# ==========================================
# 5. MAIN NAVIGATION (Sidebar Decoration Included)
# ==========================================
st.sidebar.markdown('<div class="sidebar-brand">🌿 ECOSURE PORTAL</div>', unsafe_allow_html=True)
user_role = st.sidebar.selectbox("Access Level:", ["Applicant Portal", "HR Management"])

# [DECORATION: Kotak Merah Kiri / Sidebar Stats]
st.sidebar.markdown("""
    <div style="margin-top: 30px; padding: 15px; background: rgba(255,255,255,0.6); border-radius: 15px; border: 1px solid #e0e0e0;">
        <h4 style="color: #1B4332; font-size: 1rem; margin-bottom: 10px;">🚀 System Insights</h4>
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-size: 0.8rem; color: #666;">Status:</span>
            <span style="font-size: 0.8rem; color: #2D6A4F; font-weight: bold;">Operational</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-size: 0.8rem; color: #666;">AI Latency:</span>
            <span style="font-size: 0.8rem; color: #2D6A4F; font-weight: bold;">240ms</span>
        </div>
        <hr style="margin: 10px 0; border: 0.5px solid #eee;">
        <p style="font-size: 0.75rem; color: #888; font-style: italic;">Powered by Gemini 1.5 Flash</p>
    </div>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'hr_logged_in' not in st.session_state: st.session_state['hr_logged_in'] = False
if 'user_email' not in st.session_state: st.session_state['user_email'] = ""

# ==========================================
# 6. APPLICANT PORTAL
# ==========================================
if user_role == "Applicant Portal":
    # [DECORATION: Kotak Merah Atas / Header Banner]
    st.markdown("""
        <div style="background: linear-gradient(90deg, #1B4332 0%, #2D6A4F 100%); padding: 12px 20px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: white; font-size: 0.9rem; font-weight: 600;">🌍 Sustainable Recruitment Initiative</span>
                <span style="color: #A3D9A5; font-size: 0.8rem;">Session: EXPO 2026</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state['logged_in']:
        st.title("🔐 Secure Access")
        col_auth, col_img = st.columns([1, 1.2])
        with col_auth:
            auth_mode = st.radio("Choose Mode:", ["Login", "Register"], horizontal=True)
            if auth_mode == "Login":
                email = st.text_input("Email")
                password = st.text_input("Password", type='password')
                if st.button("Sign In"):
                    conn = sqlite3.connect('ecosure.db')
                    c = conn.cursor()
                    c.execute('SELECT password FROM users WHERE email = ?', (email,))
                    data = c.fetchone()
                    conn.close()
                    if data and check_hashes(password, data[0]):
                        st.session_state['logged_in'] = True
                        st.session_state['user_email'] = email
                        st.rerun()
                    else: st.error("Access Denied.")
            else:
                new_user = st.text_input("Full Name")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type='password')
                if st.button("Register Account"):
                    conn = sqlite3.connect('ecosure.db')
                    c = conn.cursor()
                    try:
                        c.execute('INSERT INTO users(fullname, email, password) VALUES (?,?,?)', (new_user, new_email, make_hashes(new_password)))
                        conn.commit()
                        st.success("Registration Successful!")
                    except: st.error("Email already exists.")
                    conn.close()
        with col_img:
            st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800", use_container_width=True)
    else:
        st.sidebar.button("Sign Out", on_click=lambda: st.session_state.update({"logged_in": False}))
        choice = st.sidebar.radio("Navigation:", ["Job Board", "My Status"])
        
        if choice == "Job Board":
            st.title("🚀 Career Opportunities")
            c_list, c_detail = st.columns([1, 2])
            with c_list:
                sel_job = st.radio("Open Positions", list(jobs_db.keys()))
                for j_n, j_i in jobs_db.items():
                    st.markdown(f"<div class='job-card'><b>{j_n}</b><br><small>{j_i['company']}</small></div>", unsafe_allow_html=True)
            with c_detail:
                st.markdown(f"## {sel_job}")
                st.markdown(jobs_db[sel_job]['req'])
                file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
                if st.button("Submit Application"):
                    if file:
                        with st.status("AI Analysis...", expanded=True) as s:
                            binary_cv = file.getvalue()
                            text = input_pdf_text(file)
                            res = get_gemini_response(f"Score CV for {sel_job}: {text}")
                            score = int(re.search(r"(\d+)", res).group(1)) if re.search(r"(\d+)", res) else 0
                            conn = sqlite3.connect('ecosure.db')
                            conn.execute("INSERT INTO analysis_results (candidate_email, job_title, score_val, report, cv_blob) VALUES (?,?,?,?,?)", 
                                         (st.session_state['user_email'], sel_job, score, res, binary_cv))
                            conn.commit(); conn.close()
                            s.update(label="Complete!", state="complete")
                            st.balloons(); st.success("Submitted!")
        elif choice == "My Status":
            st.title("🔍 Track Progress")
            conn = sqlite3.connect('ecosure.db')
            df_status = pd.read_sql_query("SELECT * FROM analysis_results WHERE candidate_email = ?", conn, params=(st.session_state['user_email'],))
            conn.close()
            if not df_status.empty:
                for _, row in df_status.iterrows():
                    with st.container(border=True):
                        st.write(f"### {row['job_title']}")
                        if row['status'] == 'Accepted': st.success("🌳 **ACCEPTED** - Check your email!")
                        elif row['status'] == 'Rejected': st.error("🙏 **NOT SELECTED**")
                        else: st.warning("⏳ **PENDING REVIEW**")
# ==========================================
# 7. HR MANAGEMENT
# ==========================================
elif user_role == "HR Management":
    # Header Banner for HR
    st.markdown("""<div style="background: #1B4332; padding: 12px; border-radius: 12px; margin-bottom: 25px; color: white; text-align: center; font-weight: 600;">📊 HR STRATEGIC DASHBOARD</div>""", unsafe_allow_html=True)
    
    if not st.session_state['hr_logged_in']:
        st.title("🔐 Admin Verification")
        pwd = st.sidebar.text_input("HR Password:", type="password")
        if st.sidebar.button("Unlock"):
            if pwd == "admin123":
                st.session_state['hr_logged_in'] = True
                st.rerun()
    else:
        st.sidebar.button("Lock", on_click=lambda: st.session_state.update({"hr_logged_in": False}))
        if st.sidebar.button("🗑️ Reset All Data"):
            conn = sqlite3.connect('ecosure.db')
            conn.execute("DELETE FROM analysis_results")
            conn.commit(); conn.close(); st.rerun()
            
            # --- BAGIAN DECISION PANEL YANG SUDAH DIPERBAIKI ---
            with st.expander("📝 Decision Panel", expanded=True):
                st.info(f"AI Report: {cand['report']}")
                opts = ["Pending", "Accepted", "Rejected"]
                new_dec = st.radio("Verdict:", opts, index=opts.index(cand['status']) if cand['status'] in opts else 0)
                
                if st.button("Confirm Decision & Send Email"):
                    # 1. Update status di Database
                    cursor = conn.cursor()
                    cursor.execute("UPDATE analysis_results SET status = ? WHERE id = ?", (new_dec, int(cand['id'])))
                    conn.commit()
                    
                    # 2. Logika Kirim Email jika HR memilih 'Accepted'
                    if new_dec == "Accepted":
                        with st.spinner("Sending automated evaluation report..."):
                            success = send_email(
                                target_email=cand['candidate_email'], 
                                candidate_name="Candidate", 
                                score=cand['score_val'], 
                                feedback=cand['report']
                            )
                            if success:
                                st.success(f"Notification sent to {cand['candidate_email']}!")
                    
                    st.success(f"Decision updated to {new_dec}!")
                    time.sleep(1)
                    st.rerun()

        st.title("📊 Intelligence Dashboard")
        conn = sqlite3.connect('ecosure.db')
        df = pd.read_sql_query("SELECT * FROM analysis_results ORDER BY score_val DESC", conn)
        
        if not df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Applicants", len(df))
            m2.metric("Accepted", len(df[df['status']=='Accepted']))
            m3.metric("Avg Score", f"{round(df['score_val'].mean(), 1)}%")

            st.divider()
            c_bar, c_pie = st.columns([2, 1])
            color_map = {'Accepted': '#1B4332', 'Rejected': '#D32F2F', 'Pending': '#3A86FF'}
            with c_bar:
                st.plotly_chart(px.bar(df, x='candidate_email', y='score_val', color='status', color_discrete_map=color_map, title="Rankings"), use_container_width=True)
            with c_pie:
                st.plotly_chart(px.pie(df, names='status', hole=0.5, color='status', color_discrete_map=color_map), use_container_width=True)
            
            st.subheader("🏆 Leaderboard")
            st.dataframe(df[['candidate_email', 'job_title', 'score_val', 'status']], use_container_width=True)

            st.divider()
            st.subheader("📂 Review & Decisions")
            df['key'] = df['candidate_email'] + " (" + df['job_title'] + ")"
            target = st.selectbox("Select Candidate:", df['key'].unique())
            cand = df[df['key'] == target].iloc[0]

            if cand['cv_blob'] is not None:
                st.download_button(label=f"📥 Download CV - {cand['candidate_email']}", data=cand['cv_blob'], file_name=f"CV_{cand['candidate_email']}.pdf", mime="application/pdf")
            
            with st.expander("📝 Decision Panel"):
                st.info(f"AI Report: {cand['report']}")
                opts = ["Pending", "Accepted", "Rejected"]
                new_dec = st.radio("Verdict:", opts, index=opts.index(cand['status']) if cand['status'] in opts else 0)
                if st.button("Confirm Decision"):
                    cursor = conn.cursor()
                    cursor.execute("UPDATE analysis_results SET status = ? WHERE id = ?", (new_dec, int(cand['id'])))
                    conn.commit(); st.success("Updated!"); time.sleep(0.5); st.rerun()
        else: st.info("No talent data.")
        conn.close()

# ==========================================
# 8. FOOTER (Kotak Merah Bawah)
# ==========================================
# [DECORATION: Kotak Merah Bawah / Footer]
st.markdown("""
    <div style="margin-top: 50px; padding: 25px; text-align: center; border-top: 1px solid #e0e0e0;">
        <p style="color: #1B4332; font-weight: 800; font-size: 1.2rem; margin-bottom: 5px;">🌿 ECOSURE PORTAL</p>
        <p style="color: #888; font-size: 0.8rem; line-height: 1.5;">
            Empowering Green Careers through Artificial Intelligence.<br>
            Developed for <b>Sustainability EXPO 2026</b>
        </p>
        <div style="margin-top: 15px;">
            <span style="background: #E8F5E9; color: #1B4332; padding: 5px 15px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; border: 1px solid #C8E6C9;">AI SCREENING</span>
            <span style="background: #E8F5E9; color: #1B4332; padding: 5px 15px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; border: 1px solid #C8E6C9; margin-left: 8px;">SECURE DB</span>
            <span style="background: #E8F5E9; color: #1B4332; padding: 5px 15px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; border: 1px solid #C8E6C9; margin-left: 8px;">PDF PARSING</span>
        </div>
    </div>
""", unsafe_allow_html=True)