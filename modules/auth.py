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
    """Register a new user."""
    client = get_supabase_client()
    if not client:
        return {"success": False, "error": "Database not configured. Use Demo Mode instead."}
    
    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {
                "success": True,
                "user_id": response.user.id,
                "email": response.user.email,
                "message": "Account created! Please check your email to verify."
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
        return {"success": False, "error": "Database not configured. Use Demo Mode instead."}
    
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
    """Render the login/signup page."""
    st.markdown("""
    <style>
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
    }
    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="auth-header">', unsafe_allow_html=True)
    st.markdown("# 🧬 Aevum")
    st.markdown("### Longevity Health Dashboard")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check if Supabase is configured
    client = get_supabase_client()
    supabase_configured = client is not None
    
    if supabase_configured:
        # Tab selection for Login/Signup
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            render_login_form()
        
        with tab2:
            render_signup_form()
        
        st.markdown("---")
    
    # Demo mode option (always available)
    st.markdown("### 🎮 Try the Demo")
    st.markdown("No account needed - explore with sample data!")
    if st.button("Enter Demo Mode", use_container_width=True, type="primary"):
        st.session_state['authenticated'] = True
        st.session_state['user_id'] = 'demo_user'
        st.session_state['user_email'] = 'demo@aevum.app'
        st.session_state['demo_mode'] = True
        st.rerun()


def render_login_form():
    """Render the login form."""
    with st.form("login_form"):
        st.subheader("Welcome Back!")
        
        email = st.text_input("📧 Email", placeholder="your@email.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Your password")
        
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
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")


def render_signup_form():
    """Render the signup form."""
    with st.form("signup_form"):
        st.subheader("Create Your Account")
        
        email = st.text_input("📧 Email", placeholder="your@email.com", key="signup_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters", key="signup_pass")
        password_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Repeat password", key="signup_pass2")
        
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
                    st.success(f"✅ {result['message']}")
                    st.info("You can now log in with your credentials.")
                else:
                    st.error(f"❌ {result['error']}")


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
