import streamlit as st
from _pages import teacher_profile_page, student_profile_page, teacher_courses_page, student_courses_page, teacher_virtual_class_page, student_virtual_class_page

def show():
    if 'dashboard_selection' not in st.session_state:
        st.session_state['dashboard_selection'] = 'profile' # Default to profile page

    user_type = st.session_state['user_type'] # Directly access user_type
    print(f"DEBUG: User type retrieved in dashboard_page: {user_type}")
    first_name = st.session_state.get('first_name', 'Kullanıcı')
    last_name = st.session_state.get('last_name', '')

    st.title(f"Hoş Geldin, {first_name} {last_name} ({user_type.capitalize()})!")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Profil", key="dashboard_profile_btn"):
            st.session_state['dashboard_selection'] = 'profile'
    with col2:
        if st.button("Dersler", key="dashboard_courses_btn"):
            st.session_state['dashboard_selection'] = 'courses'
    with col3:
        if st.button("Sanal Sınıf Modülü", key="dashboard_virtual_class_btn"):
            st.session_state['dashboard_selection'] = 'virtual_class'

    st.sidebar.title("Navigasyon")
    if st.sidebar.button("Çıkış Yap"):
        st.session_state['logged_in'] = False
        st.session_state['first_name'] = None
        st.session_state['last_name'] = None
        st.session_state['user_type'] = None
        st.session_state['user_id'] = None
        st.session_state['teacher_id'] = None
        st.session_state['student_id'] = None
        st.session_state['branch'] = None
        st.session_state['class'] = None
        st.session_state['page'] = 'login' # Redirect to login page
        st.rerun()

    # Render selected dashboard sub-page
    if st.session_state['dashboard_selection'] == 'profile':
        if user_type == 'öğretmen':
            teacher_profile_page.show()
        elif user_type == 'öğrenci':
            student_profile_page.show()
    elif st.session_state['dashboard_selection'] == 'courses':
        if user_type == 'öğretmen':
            teacher_courses_page.show()
        elif user_type == 'öğrenci':
            student_courses_page.show()
    elif st.session_state['dashboard_selection'] == 'virtual_class':
        if user_type == 'öğretmen':
            teacher_virtual_class_page.show()
        elif user_type == 'öğrenci':
            student_virtual_class_page.show()
