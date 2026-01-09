"""
Authentication Module - Supabase Integration
Handles user login, signup, and session management.
"""
import streamlit as st
from typing import Optional, Dict
import json
from datetime import datetime

# Try to import supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None


def get_supabase_client() -> Optional[Client]:
    """Initialize and return Supabase client."""
    if not SUPABASE_AVAILABLE:
        return None
    
    try:
        # Try multiple ways to get secrets (Streamlit Cloud compatibility)
        url = None
        key = None
        
        # Method 1: Direct access
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        except:
            pass
        
        # Method 2: Get method
        if not url or not key:
            try:
                url = st.secrets.get("SUPABASE_URL")
                key = st.secrets.get("SUPABASE_KEY")
            except:
                pass
        
        if not url or not key:
            return None
        
        return create_client(url, key)
    except Exception as e:
        return None


def signup_user(email: str, password: str) -> Dict:
    """Register a new user and auto-login (no email confirmation needed)."""
    client = get_supabase_client()
    if not client:
        return {"success": False, "error": "Database not configured. Please configure database credentials."}
    
    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "email_redirect_to": None
            }
        })
        
        if response.user:
            # Auto-login: set session state directly
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = response.user.id
            st.session_state['user_email'] = email
            return {
                "success": True,
                "user_id": response.user.id,
                "email": response.user.email,
                "auto_login": True
            }
        else:
            return {"success": False, "error": "Signup failed. Try again."}
    
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return {"success": False, "error": "Email already registered. Try logging in."}
        return {"success": False, "error": error_msg}


def login_user(email: str, password: str) -> Dict:
    """Authenticate an existing user."""
    client = get_supabase_client()
    if not client:
        return {"success": False, "error": "Database not configured. Please configure database credentials."}
    
    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {
                "success": True,
                "user_id": response.user.id,
                "email": response.user.email,
                "access_token": response.session.access_token if response.session else None
            }
        else:
            return {"success": False, "error": "Invalid credentials"}
    
    except Exception as e:
        error_msg = str(e)
        if "email not confirmed" in error_msg.lower():
            # Bypass: login anyway by setting session directly
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = f"unconfirmed_{email}"
            st.session_state['user_email'] = email
            return {"success": True, "user_id": f"unconfirmed_{email}", "email": email, "bypassed": True}
        if "invalid" in error_msg.lower():
            return {"success": False, "error": "Invalid email or password"}
        return {"success": False, "error": error_msg}


def logout_user():
    """Log out the current user."""
    # Clear session state
    for key in ['user', 'user_id', 'user_email', 'authenticated']:
        if key in st.session_state:
            del st.session_state[key]
    
    client = get_supabase_client()
    if client:
        try:
            client.auth.sign_out()
        except:
            pass


def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[Dict]:
    """Get current logged-in user info."""
    if is_authenticated():
        return {
            "user_id": st.session_state.get('user_id'),
            "email": st.session_state.get('user_email')
        }
    return None


def render_auth_page():
    """Render the login/signup page with WHOOP-inspired design."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800&display=swap');
    
    .login-logo {
        font-size: 3.5rem;
        font-weight: 800;
        color: #00f0ff;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 20px rgba(0, 240, 255, 0.5); }
        50% { text-shadow: 0 0 40px rgba(0, 240, 255, 0.8), 0 0 60px rgba(0, 240, 255, 0.4); }
    }
    
    .login-logo { animation: fadeInUp 0.6s ease-out, glow 3s ease-in-out infinite; }
    
    .login-subtitle {
        color: #6b7280;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 2.5rem;
        animation: fadeInUp 0.6s ease-out 0.1s backwards;
    }
    
    .feature-list {
        text-align: left;
        margin: 2rem 0;
        padding: 1.5rem;
        background: #141414;
        border-radius: 12px;
        border: 1px solid #222222;
        animation: fadeInUp 0.6s ease-out 0.3s backwards;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem 0;
        color: #9ca3af;
        font-size: 0.9rem;
        font-family: 'Nunito', sans-serif;
        border-bottom: 1px solid #1a1a1a;
    }
    
    .feature-item:last-child { border-bottom: none; }
    
    .feature-dot {
        width: 8px;
        height: 8px;
        background: #00f0ff;
        border-radius: 50%;
        flex-shrink: 0;
    }
    
    .divider-text {
        color: #4b5563;
        font-size: 0.8rem;
        margin: 1.5rem 0;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-family: 'Nunito', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0 2rem 0;">
            <div class="login-logo">aevum</div>
            <div class="login-subtitle">longevity analytics platform</div>
        </div>
        """, unsafe_allow_html=True)
        
        client = get_supabase_client()
        supabase_configured = client is not None
        
        if supabase_configured:
            tab1, tab2 = st.tabs(["Sign In", "Create Account"])
            with tab1:
                render_login_form()
            with tab2:
                render_signup_form()
        else:
            # No Supabase - allow guest access
            st.info("Sign in to save your data across sessions")
            if st.button("Continue as Guest", use_container_width=True, type="primary"):
                st.session_state['authenticated'] = True
                st.session_state['user_id'] = 'guest_user'
                st.session_state['user_email'] = 'guest@aevum.app'
                st.rerun()
        
        st.markdown("""
        <div class="feature-list">
            <div class="feature-item"><span class="feature-dot"></span> Blood biomarker analysis with longevity ranges</div>
            <div class="feature-item"><span class="feature-dot"></span> Wearable biometrics integration</div>
            <div class="feature-item"><span class="feature-dot"></span> Biological age estimation</div>
            <div class="feature-item"><span class="feature-dot"></span> Personalized health protocols</div>
        </div>
        """, unsafe_allow_html=True)



def render_login_form():
    """Render the login form."""
    with st.form("login_form"):
        st.subheader("Welcome Back!")
        
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Your password")
        
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
        
        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                with st.spinner("Logging in..."):
                    result = login_user(email, password)
                
                if result["success"]:
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = result['user_id']
                    st.session_state['user_email'] = result['email']
                    st.session_state['demo_mode'] = False
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(f"{result['error']}")


def render_signup_form():
    """Render the signup form."""
    with st.form("signup_form"):
        st.subheader("Create Your Account")
        
        email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_pass")
        password_confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="signup_pass2")
        
        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            elif password != password_confirm:
                st.error("Passwords don't match")
            else:
                with st.spinner("Creating account..."):
                    result = signup_user(email, password)
                
                if result["success"]:
                    st.success(f"{result['message']}")
                    st.info("You can now log in with your credentials.")
                else:
                    st.error(f"{result['error']}")


def save_user_data(data_type: str, data: dict) -> bool:
    """Save user-specific data to Supabase."""
    if st.session_state.get('demo_mode'):
        # In demo mode, just save to session state
        if 'demo_data' not in st.session_state:
            st.session_state['demo_data'] = {}
        st.session_state['demo_data'][data_type] = data
        return True
    
    client = get_supabase_client()
    if not client:
        return False
    
    user_id = st.session_state.get('user_id')
    if not user_id:
        return False
    
    try:
        # Upsert data (insert or update)
        client.table('user_health_data').upsert({
            'user_id': user_id,
            'data_type': data_type,
            'data': json.dumps(data),
            'updated_at': datetime.utcnow().isoformat()
        }).execute()
        return True
    except Exception as e:
        return False


def load_user_data(data_type: str) -> Optional[dict]:
    """Load user-specific data from Supabase."""
    if st.session_state.get('demo_mode'):
        return st.session_state.get('demo_data', {}).get(data_type)
    
    client = get_supabase_client()
    if not client:
        return None
    
    user_id = st.session_state.get('user_id')
    if not user_id:
        return None
    
    try:
        response = client.table('user_health_data').select('data').eq(
            'user_id', user_id
        ).eq('data_type', data_type).single().execute()
        
        if response.data:
            return json.loads(response.data['data'])
        return None
    except:
        return None
