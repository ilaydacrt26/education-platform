import streamlit as st
from _pages import login_page, dashboard_page, register_page, teacher_profile_page, student_profile_page, teacher_courses_page, student_courses_page, teacher_virtual_class_page, student_virtual_class_page
from utils.db import init_db

def main():
    init_db() # Uygulama başladığında veritabanını başlat

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login' # Varsayılan olarak giriş sayfası

    if st.session_state['logged_in']:
        dashboard_page.show()
    elif st.session_state['page'] == 'register':
        register_page.show()
    else:
        login_page.show()

if __name__ == '__main__':
    main()
