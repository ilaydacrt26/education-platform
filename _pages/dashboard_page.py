import streamlit as st

def show():
    st.title("Öğrenci Paneli")
    st.write(f"Hoş geldin, {st.session_state.get('username', 'Kullanıcı')}!")

    st.sidebar.title("Navigasyon")
    if st.sidebar.button("Çıkış Yap"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None # Kullanıcı adını temizle
        st.rerun()

    st.header("Devam Eden Derslerim")
    st.write("Burada devam eden dersleriniz listelenecek.")

    st.header("İlerleme Durumu")
    st.write("Genel ilerleme durumunuzu buradan takip edebilirsiniz.")

    st.header("Duyurular")
    st.write("Yeni duyurular burada gösterilecek.")
