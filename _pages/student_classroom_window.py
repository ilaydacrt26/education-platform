import streamlit as st
from datetime import datetime

def show():
    st.title("🎓 Sanal Sınıf - Öğrenci Paneli")
    
    # Check if there's an active join request
    if not st.session_state.get('join_request'):
        st.error("Aktif bir katılım isteğiniz bulunamadı.")
        return
    
    request = st.session_state['join_request']
    st.success(f"🟢 Katıldığınız Sınıf: {request['class_name']}")
    st.info(f"Davet Kodu: `{request['invite_code']}` - Sanal sınıf ortamında derse katılıyorsunuz")
    
    # Student controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        camera_status = st.session_state.get('student_camera', True)
        if st.button("📹 Kamera", key="student_toggle_camera"):
            st.session_state['student_camera'] = not camera_status
            st.rerun()
        st.write("🟢 Açık" if camera_status else "🔴 Kapalı")
    
    with col2:
        mic_status = st.session_state.get('student_mic', True)
        if st.button("🎤 Mikrofon", key="student_toggle_mic"):
            st.session_state['student_mic'] = not mic_status
            st.rerun()
        st.write("🟢 Açık" if mic_status else "🔴 Kapalı")
    
    with col3:
        if st.button("🚪 Sınıftan Ayrıl", type="primary"):
            del st.session_state['in_student_classroom']
            st.success("Sınıftan ayrıldınız.")
            st.rerun()
    
    st.markdown("---")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Canlı Yayın")
        st.info("🎥 Öğretmenin yayını burada görünecek")
        st.info("👂 Ses yayını aktif")
        
        # Student video preview
        if st.session_state.get('student_camera', True):
            st.info("📹 Kamera açık - Görüntünüz öğretmene görünüyor")
        else:
            st.warning("📹 Kamera kapalı")
    
    with col2:
        st.subheader("👥 Katılımcılar")
        st.write("• Öğretmen")
        st.write(f"• {request['student_name']} (Siz)")
        st.write("• Diğer öğrenciler...")
    
    # Chat section
    st.markdown("---")
    st.subheader("💬 Sınıf Sohbeti")
    
    # Initialize chat
    if 'student_classroom_chat' not in st.session_state:
        st.session_state['student_classroom_chat'] = []
    
    # Chat input
    chat_input = st.text_input("Mesajınızı yazın...", key="student_chat_input")
    if st.button("Gönder", key="send_student_message"):
        if chat_input:
            st.session_state['student_classroom_chat'].append({
                'user': request['student_name'],
                'message': chat_input,
                'time': datetime.now().strftime("%H:%M")
            })
            st.rerun()
    
    # Display messages
    for msg in st.session_state['student_classroom_chat'][-10:]:
        st.write(f"**{msg['user']} ({msg['time']}):** {msg['message']}")
