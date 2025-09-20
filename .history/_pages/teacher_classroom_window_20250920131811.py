import streamlit as st
from utils.db import get_db_connection, get_pending_requests_for_class, update_request_status
import time

def show():
    st.title("🎓 Sanal Sınıf - Öğretmen Paneli")
    
    # Check if there's an active class
    if not st.session_state.get('active_class'):
        st.error("Aktif bir sanal sınıf bulunamadı.")
        return
    
    active_class = st.session_state['active_class']
    st.success(f"🟢 Aktif Sınıf: {active_class['name']}")
    
    # Display invite code and password
    if 'password' in active_class:
        st.info(f"Davet Kodu: `{active_class['invite_code']}` | Şifre: `{active_class['password']}` - Öğrenciler bu bilgileri kullanarak katılabilir")
    else:
        st.info(f"Davet Kodu: `{active_class['invite_code']}` - Öğrenciler bu kodu kullanarak katılabilir")
    
    # Initialize pending requests
    if 'pending_requests' not in st.session_state:
        st.session_state['pending_requests'] = []
    
    # Initialize approved students
    if 'approved_students' not in st.session_state:
        st.session_state['approved_students'] = []
    
    # Initialize classroom chat
    if 'classroom_chat' not in st.session_state:
        st.session_state['classroom_chat'] = []
    
    # Teacher controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        camera_status = st.session_state.get('teacher_camera', True)
        if st.button("📹 Kamera", key="toggle_camera"):
            st.session_state['teacher_camera'] = not camera_status
            st.rerun()
        st.write("🟢 Açık" if camera_status else "🔴 Kapalı")
    
    with col2:
        mic_status = st.session_state.get('teacher_mic', True)
        if st.button("🎤 Mikrofon", key="toggle_mic"):
            st.session_state['teacher_mic'] = not mic_status
            st.rerun()
        st.write("🟢 Açık" if mic_status else "🔴 Kapalı")
    
    with col3:
        screen_status = st.session_state.get('teacher_screen', False)
        if st.button("🖥️ Ekran Paylaş", key="toggle_screen"):
            st.session_state['teacher_screen'] = not screen_status
            st.rerun()
        st.write("🟢 Paylaşılıyor" if screen_status else "🔴 Kapalı")
    
    with col4:
        if st.button("🔴 Sınıfı Sonlandır", type="primary"):
            del st.session_state['active_class']
            del st.session_state['pending_requests']
            del st.session_state['approved_students']
            del st.session_state['classroom_chat']
            st.success("Sınıf sonlandırıldı.")
            st.rerun()
    
    st.markdown("---")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Canlı Yayın")
        if st.session_state.get('teacher_camera', True):
            st.info("🎥 Kamera açık - Video yayını burada görünecek")
        else:
            st.warning("📹 Kamera kapalı")
        
        if st.session_state.get('teacher_screen', False):
            st.info("🖥️ Ekran paylaşımı aktif")
        
        # Approved students video area
        if st.session_state['approved_students']:
            st.subheader("👥 Öğrenci Görüntüleri")
            for student in st.session_state['approved_students']:
                st.write(f"📹 {student['name']} - Kamera açık")
    
    with col2:
        st.subheader("📋 Katılım İstekleri")
        
        # Real-time refresh for join requests
        col_refresh, col_info = st.columns([1, 3])
        with col_refresh:
            if st.button("🔄 İstekleri Yenile"):
                st.rerun()
        with col_info:
            st.caption("Öğrenciler katılım isteği gönderdiğinde burada görünecek")
        
        # Fetch real pending requests from database
        active_class = st.session_state['active_class']
        pending_requests = get_pending_requests_for_class(active_class['id'])
        
        
        if pending_requests:
            for request in pending_requests:
                col_req, col_approve, col_reject = st.columns([2, 1, 1])
                with col_req:
                    request_time = request['request_time'].split(' ')[1][:5] if ' ' in request['request_time'] else request['request_time']
                    st.write(f"👤 {request['student_name']} ({request['student_class']}) - {request_time}")
                with col_approve:
                    if st.button("✅", key=f"approve_{request['id']}"):
                        # Update status in database
                        if update_request_status(request['id'], 'approved'):
                            # Move to approved students
                            st.session_state['approved_students'].append({
                                'id': request['id'],
                                'name': request['student_name'],
                                'class': request['student_class']
                            })
                            st.success(f"{request['student_name']} onaylandı!")
                            st.rerun()
                        else:
                            st.error("Onaylama işlemi başarısız!")
                with col_reject:
                    if st.button("❌", key=f"reject_{request['id']}"):
                        # Update status in database
                        if update_request_status(request['id'], 'rejected'):
                            st.warning(f"{request['student_name']} reddedildi!")
                            st.rerun()
                        else:
                            st.error("Reddetme işlemi başarısız!")
        else:
            st.info("📭 Bekleyen katılım isteği yok - Öğrenciler davet kodunu ve şifreyi kullanarak katılım isteği gönderebilir")
        
        st.markdown("---")
        st.subheader("👥 Onaylanan Öğrenciler")
        if st.session_state['approved_students']:
            for student in st.session_state['approved_students']:
                col_student, col_kick = st.columns([3, 1])
                with col_student:
                    st.write(f"✅ {student['name']} ({student['class']})")
                with col_kick:
                    if st.button("🚪", key=f"kick_{student['id']}"):
                        st.session_state['approved_students'] = [
                            s for s in st.session_state['approved_students'] 
                            if s['id'] != student['id']
                        ]
                        st.warning(f"{student['name']} sınıftan çıkarıldı!")
                        st.rerun()
        else:
            st.info("Henüz onaylanan öğrenci yok")
    
    # Chat section
    st.markdown("---")
    st.subheader("💬 Sınıf Sohbeti")
    
    # Chat input
    chat_input = st.text_input("Mesajınızı yazın...", key="teacher_chat_input")
    if st.button("Gönder", key="send_teacher_message"):
        if chat_input:
            st.session_state['classroom_chat'].append({
                'user': 'Öğretmen',
                'message': chat_input,
                'time': time.strftime("%H:%M")
            })
            st.rerun()
    
    # Display messages
    for msg in st.session_state['classroom_chat'][-10:]:
        st.write(f"**{msg['user']} ({msg['time']}):** {msg['message']}")
    
    # Note: Auto-refresh removed for better user experience
    # In a real-time app, you would use WebSockets or similar technology
