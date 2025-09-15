import streamlit as st
from _pages import login_page, dashboard_page
from utils.db import init_db

def main():
    init_db() # Uygulama başladığında veritabanını başlat

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None

    if st.session_state['logged_in']:
        dashboard_page.show()
    else:
        login_page.show()

if __name__ == '__main__':
    main()
