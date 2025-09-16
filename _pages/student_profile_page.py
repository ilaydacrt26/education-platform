import streamlit as st

def show():
    st.title("Öğrenci Profil Sayfası")
    st.write("Burada kendi gelişiminizi ve raporlarınızı görüntüleyebilirsiniz.")

    st.subheader("Gelişim Grafiklerim")
    st.info("Derslere katılım, test skorları ve ödev tamamlama gibi gelişim grafikleriniz burada gösterilecektir.")

    st.subheader("Raporlarım")
    st.info("Eğitim performansınıza dair detaylı raporlar burada listelenecektir.")
