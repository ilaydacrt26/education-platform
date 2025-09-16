import streamlit as st
from utils.auth import register_teacher, register_student
import re

def validate_password(password):
    if len(password) < 6 or len(password) > 20:
        return False, "Şifre en az 6, en fazla 20 karakter uzunluğunda olmalıdır."
    if not re.search(r"[A-Z]", password):
        return False, "Şifre en az bir büyük harf, bir küçük harf, bir rakam ve bir özel karakter içermelidir."
    if not re.search(r"[a-z]", password):
        return False, "Şifre en az bir büyük harf, bir küçük harf, bir rakam ve bir özel karakter içermelidir."
    if not re.search(r"[0-9]", password):
        return False, "Şifre en az bir büyük harf, bir küçük harf, bir rakam ve bir özel karakter içermelidir."
    if not re.search(r"[^a-zA-Z0-9]", password):
        return False, "Şifre en az bir büyük harf, bir küçük harf, bir rakam ve bir özel karakter içermelidir."
    return True, ""

def show():
    st.title("Kayıt Ol")

    user_type = st.radio("Kullanıcı Tipi Seçin:", ("Öğrenci", "Öğretmen"), key="register_user_type")

    st.subheader("Yeni Kayıt")
    new_first_name = st.text_input("Adınız", key="register_first_name")
    new_last_name = st.text_input("Soyadınız", key="register_last_name")
    new_email = st.text_input("E-posta", key="register_email")

    if user_type == "Öğretmen":
        new_branch = st.selectbox("Branşınız", ["Matematik", "Türkçe", "Fen", "İngilizce", "Tarih", "Coğrafya", "Bilişim"], key="register_branch")
    else: # Öğrenci
        new_class = st.selectbox("Sınıfınız", list(range(1, 13)), key="register_class")

    new_password = st.text_input("Yeni Şifre", type="password", key="register_password")
    confirm_password = st.text_input("Şifreyi Onayla", type="password", key="confirm_password")

    if st.button("Kayıt Ol", key="register_button"):
        if new_password != confirm_password:
            st.error("Şifreler eşleşmiyor.")
        else:
            is_valid, message = validate_password(new_password)
            if not is_valid:
                st.error(message)
            else:
                if user_type == "Öğretmen":
                    if register_teacher(new_first_name, new_last_name, new_email, new_branch, new_password):
                        st.success("Kayıt başarılı! Lütfen giriş yapın.")
                        st.session_state['page'] = 'login'
                        st.rerun()
                    else:
                        st.error("E-posta zaten kullanımda.")
                else: # Öğrenci
                    if register_student(new_first_name, new_last_name, new_class, new_email, new_password):
                        st.success("Kayıt başarılı! Lütfen giriş yapın.")
                        st.session_state['page'] = 'login'
                        st.rerun()
                    else:
                        st.error("E-posta zaten kullanımda.")

    st.markdown("Zaten bir hesabınız var mı?")
    if st.button("Giriş Sayfasına Git", key="go_to_login"):
        st.session_state['page'] = 'login'
        st.rerun()
