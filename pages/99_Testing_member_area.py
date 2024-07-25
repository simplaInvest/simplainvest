import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Supabase credentials
SUPABASE_URL = 'https://kcbmrsrddmxgaewnwqxg.supabase.co'  # Your Supabase project URL
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjYm1yc3JkZG14Z2Fld253cXhnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjE2MDIyODAsImV4cCI6MjAzNzE3ODI4MH0.QVtexhpShu440CvcGUY1SBCtqxQaY8lhRoij3zJLmiA'  # Replace with your Supabase public anon key
ADMIN_EMAIL = 'working.milazzo@gmail.com'
ADMIN_PASSWORD = 'Pdl@123!'


# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit page configuration
st.set_page_config(layout="wide", page_title="Área de Membros", page_icon="💎")

# Function to check if the email is already registered
def is_email_registered(email):
    try:
        response = supabase.table('Testing Supabase').select('email').eq('email', email).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Erro na função is_email_registered: {str(e)}")
        logging.error(f"Erro na função is_email_registered: {str(e)}")
        return False

# Function to sign up user and insert data into Supabase table
def sign_up_user(email, senha):
    try:
        if is_email_registered(email):
            st.warning("This email is already registered. Please use a different email or log in.")
            logging.warning("This email is already registered.")
            return None

        response = supabase.auth.sign_in_with_password({
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        })
        if response.user:
            logging.info(f"User {email} signed up successfully")
            # Insert user data into the table
            logging.info(f"Inserting user data into table: email={email}, senha={senha}")
            supabase.table('Testing Supabase').insert({
                "email": email,
                "senha": senha,  # Note: It's better to hash passwords before storing them
                "created_at": datetime.now().isoformat()
            }).execute()
        return response
    except Exception as e:
        st.error(f"Erro na função sign_up_user: {str(e)}")
        logging.error(f"Erro na função sign_up_user: {str(e)}")
        return None

# Function to sign in user
def sign_in_user(email, senha):
    try:
        logging.info(f"Attempt to sign in user: {ADMIN_EMAIL}")
        response = supabase.auth.sign_in_with_password({
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        })
        if response.user:
            response_login = supabase.table('Testing Supabase').select('*').eq('email', email).eq('senha', senha).neq('email', '').execute()
            if response_login.data:
                logging.info(f"User {email} signed in successfully")
                st.session_state['logged_in'] = True
                st.session_state['user'] = response_login
                return response_login
            else:
                logging.warning(f"User {email} not found")
                return { 'error': 'Usuário não encontrado', 'code': 'USER_NOT_FOUND' }
        else:
            logging.warning(f"Credenciais para {email} inválidas")
        return response
    except Exception as e:
        logging.error(f"Erro na função sign_in_user: {str(e)}")
        return None

# Function to sign out user
def sign_out_user():
    try:
        supabase.auth.sign_out()
        logging.info("User signed out")
    except Exception as e:
        st.error(f"Erro na função sign_out_user: {str(e)}")
        logging.error(f"Erro na função sign_out_user: {str(e)}")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'register_in_progress' not in st.session_state:
    st.session_state['register_in_progress'] = False

# Registration page
def show_registration():
    st.header('Register')
    email_reg = st.text_input('Email (Register)', key='email_reg')
    senha_reg = st.text_input('Senha (Register)', type='password', key='senha_reg')
    register_button = st.button('Register', disabled=st.session_state['register_in_progress'])

    if register_button and not st.session_state['register_in_progress']:
        st.session_state['register_in_progress'] = True
        response = sign_up_user(email_reg, senha_reg)
        if response and response.user:
            st.success('User registered successfully')
        st.session_state['register_in_progress'] = False

# Login page
def show_login():
    st.header('Login')
    email_login = st.text_input('Email (Login)', key='email_login')
    senha_login = st.text_input('Senha (Login)', type='password', key='senha_login')
    if st.button('Login'):
        response = sign_in_user(email_login, senha_login)
        if response and hasattr(response, 'data'):
            st.success('Login successful')
            show_main_app()
        elif response and 'code' in response:
            st.error('Email ou senha inválidos')
        else:
            st.error('Algo deu errado... (verifique sua autenticação na API)')

# Main app content
def show_main_app():
    st.write(f"Welcome, {st.session_state['user'].data[0]['email']}!")
    st.write("Hello World")
    if st.button('Logout'):
        sign_out_user()
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.experimental_rerun()

# Render the appropriate page based on login state
if st.session_state['logged_in']:
    show_main_app()
else:
    option = st.selectbox('Choose an option', ['Login', 'Register'])
    if option == 'Login':
        show_login()
    else:
        show_registration()
