# app.py

import streamlit as st
from rag_system import HRISRagSystem
import os
from dotenv import load_dotenv
from laravel_api_client import LaravelHRISAPI

load_dotenv()

# Page config
st.set_page_config(
    page_title="HRIS Chatbot PT. XYZ",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #f5f7fa; }
    .stChatMessage { 
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOGIN SYSTEM ====================

def login_page():
    """Login page"""
    st.title("🔐 Login - HRIS Chatbot")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Silakan Login")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="user@company.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("❌ Email dan password harus diisi!")
                    return
                
                # Initialize API client
                api_client = LaravelHRISAPI(
                    base_url=os.getenv('LARAVEL_API_URL', 'http://127.0.0.1:8000/api')
                )
                
                # Login
                with st.spinner("🔄 Logging in..."):
                    result = api_client.login(email, password)
                
                if result.get('success'):
                    # Save to session
                    st.session_state.logged_in = True
                    st.session_state.access_token = result['data']['token']
                    st.session_state.user_data = result['data']['user']
                    
                    st.success(f"✅ Login berhasil! Selamat datang, {result['data']['user']['name']}")
                    st.rerun()
                else:
                    st.error(f"❌ Login gagal: {result.get('message', 'Invalid credentials')}")
        
        # Demo credentials hint
        with st.expander("ℹ️ Demo Credentials"):
            st.markdown("""
            **Test Accounts:**
            - Admin: `admin@company.com` / `admin123`
            - Manager: `sarah@company.com` / `password123`
            - Employee: `john@company.com` / `password123`
            """)

def logout():
    """Logout function"""
    # Call logout API
    if 'access_token' in st.session_state:
        api_client = LaravelHRISAPI(
            base_url=os.getenv('LARAVEL_API_URL', 'http://127.0.0.1:8000/api'),
            access_token=st.session_state.access_token
        )
        api_client.logout()
    
    # Clear session
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.rerun()

# ==================== MAIN APP ====================

def main_app():
    """Main chatbot interface (after login)"""
    
    # Header with user info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🤖 HRIS Chatbot PT. XYZ")
        st.markdown(f"**Halo, {st.session_state.user_data['name']}!** 👋")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    st.markdown("---")
    
    # Initialize RAG system with token
    @st.cache_resource
    def init_rag_system(_access_token):
        """Initialize RAG system with user token"""
        groq_api_key = os.getenv("GROQ_API_KEY")
        laravel_api_url = os.getenv('LARAVEL_API_URL', 'http://127.0.0.1:8000/api')
        
        return HRISRagSystem(
            groq_api_key=groq_api_key,
            laravel_api_url=laravel_api_url,
            access_token=_access_token
        )
    
    rag_system = init_rag_system(st.session_state.access_token)
    
    # Sidebar
    with st.sidebar:
        st.header("👤 Info Karyawan")
        
        user = st.session_state.user_data
        st.markdown(f"""
        **ID:** {user.get('employee_id', 'N/A')}  
        **Nama:** {user['name']}  
        **Email:** {user['email']}  
        **Department:** {user.get('employee', {}).get('department', 'N/A')}  
        **Position:** {user.get('employee', {}).get('position', 'N/A')}  
        **Role:** {user.get('role', 'employee').upper()}
        """)
        
        st.markdown("---")
        
        # Quick info from API
        st.header("📊 Quick Info")
        
        with st.spinner("Loading..."):
            # Get attendance summary
            summary = rag_system.api_client.get_my_attendance_summary()
            
            if summary.get('success'):
                data = summary['data']
                st.metric("Kehadiran Bulan Ini", f"{data['present']} hari")
                st.metric("Terlambat", f"{data['late']} kali")
                st.metric("Attendance Rate", f"{data['attendance_rate']}%")
            
            # Get leave balance
            balance = rag_system.api_client.get_my_leave_balance()
            
            if balance.get('success'):
                leave_data = balance['data']['annual_leave']
                st.metric("Sisa Cuti", f"{leave_data['remaining']} hari")
        
        st.markdown("---")
        
        # Quick actions
        st.header("🚀 Quick Questions")
        
        quick_questions = [
            "Sisa cuti saya berapa?",
            "Absensi bulan ini gimana?",
            "Cara ajukan cuti?",
            "Jam kerja berapa?",
        ]
        
        for question in quick_questions:
            if st.button(question, key=f"quick_{question}", use_container_width=True):
                st.session_state.quick_question = question
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"""Halo {st.session_state.user_data['name']}! 👋

Saya asisten virtual HR PT. XYZ. Saya bisa membantu Anda dengan:

✅ **Info Personal Anda:**
- Sisa cuti tahunan
- Ringkasan absensi bulan ini
- Riwayat kehadiran

✅ **Informasi Umum:**
- Kebijakan cuti & jam kerja
- Prosedur pengajuan cuti
- Benefit karyawan

Silakan tanya apa saja! 😊"""
        })
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle quick question
    if "quick_question" in st.session_state:
        prompt = st.session_state.quick_question
        del st.session_state.quick_question
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("💭 Sedang berpikir..."):
                response = rag_system.chat(prompt)
                st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("💬 Ketik pertanyaan Anda..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("💭 Sedang berpikir..."):
                response = rag_system.chat(prompt)
                st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ==================== APP ENTRY POINT ====================

def main():
    # Check if logged in
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()