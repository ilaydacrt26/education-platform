import streamlit as st
from utils.auth import login_user

def show():
    st.title("Giriş Yap")

    user_type = st.radio("Kullanıcı Tipi Seçin:", ("Öğrenci", "Öğretmen"), key="login_user_type")

    st.subheader(f"{user_type} Girişi")
    login_first_name = st.text_input("Adınız", key="login_first_name")
    login_last_name = st.text_input("Soyadınız", key="login_last_name")
    login_password = st.text_input("Şifre", type="password", key="login_password")
    if st.button("Giriş Yap", key="login_button"):
        if user_type == "Öğretmen":
            user = login_user("teacher", login_first_name, login_last_name, login_password)
        else: # Öğrenci
            user = login_user("student", login_first_name, login_last_name, login_password)

        if user:
            st.session_state['logged_in'] = True
            st.session_state['first_name'] = user['first_name']
            st.session_state['last_name'] = user['last_name']
            st.session_state['user_type'] = user_type.lower() # 'öğretmen' or 'öğrenci'
            if user_type == "Öğretmen":
                st.session_state['branch'] = user['branch']
                st.session_state['teacher_id'] = user['id'] # Store teacher_id
            else: # Öğrenci
                st.session_state['class'] = user['class']
                st.session_state['student_id'] = user['id'] # Store student_id
            st.success(f"Hoş geldin, {user['first_name']} {user['last_name']}!")
            st.rerun()
        else:
            st.error("Yanlış ad/soyad veya şifre.")

    st.markdown("Hesabınız yok mu?")
    if st.button("Kayıt Sayfasına Git", key="go_to_register"):
        st.session_state['page'] = 'register'
        st.rerun()
