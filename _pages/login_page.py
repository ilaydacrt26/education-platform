import streamlit as st
from utils.auth import register_user, login_user

def show():
    st.title("Giriş Yap / Kayıt Ol")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Giriş Yap")
        login_username_email = st.text_input("Kullanıcı Adı veya E-posta")
        login_password = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            user = login_user(login_username_email, login_password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['username'] = user['username'] # Kullanıcı adını session'a kaydet
                st.success(f"Hoş geldin, {user['username']}!")
                st.rerun()
            else:
                st.error("Yanlış kullanıcı adı/e-posta veya şifre.")

    with col2:
        st.subheader("Kayıt Ol")
        new_username = st.text_input("Yeni Kullanıcı Adı")
        new_email = st.text_input("E-posta")
        new_password = st.text_input("Yeni Şifre", type="password")
        confirm_password = st.text_input("Şifreyi Onayla", type="password")

        if st.button("Kayıt Ol"):
            if new_password == confirm_password:
                if register_user(new_username, new_email, new_password):
                    st.success("Kayıt başarılı! Lütfen giriş yapın.")
                else:
                    st.error("Kullanıcı adı veya e-posta zaten kullanımda.")
            else:
                st.error("Şifreler eşleşmiyor.")
