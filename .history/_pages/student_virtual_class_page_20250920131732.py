import streamlit as st
from utils.db import get_db_connection, get_pending_requests_for_class, get_request_status, update_request_status, get_student_requests, get_student_approved_classes, create_student_join_request
import bcrypt
import calendar as py_calendar
from datetime import date as dt_date, datetime

def show():
    st.title("Öğrenci Sanal Sınıf Modülü")
    st.write("Burada derslere katılabilir ve takvimi görüntüleyebilirsiniz.")

    # Sanal Sınıfa Katılım İsteği
    st.subheader("Sanal Sınıfa Katılım İsteği")
    with st.form(key='join_request_form'):
        st.write("Sanal sınıfa katılmak için davet kodunu ve şifreyi girin:")
        invite_code_input = st.text_input("Davet Kodu Girin", placeholder="Örn: ABC12345")
        class_password_input = st.text_input("Sınıf Şifresi", type="password")
        student_class = st.text_input("Sınıfınız", placeholder="Örn: 9A")
        join_button = st.form_submit_button(label='Katılım İsteği Gönder')
        
        if join_button:
            # Check if there's already a pending request
            if st.session_state.get('join_request') and st.session_state['join_request'].get('status') == 'pending':
                st.warning("Zaten bekleyen bir katılım isteğiniz var. Lütfen mevcut isteğinizin durumunu kontrol edin.")
            elif not invite_code_input or not class_password_input or not student_class:
                st.error("Lütfen tüm alanları doldurun.")
            else:
                # Check if class exists and password is correct
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM virtual_classes 
                    WHERE invite_code = ?
                ''', (invite_code_input,))
                
                class_data = cursor.fetchone()
                conn.close()
                
                if class_data and bcrypt.checkpw(class_password_input.encode('utf-8'), class_data['password'].encode('utf-8')):
                    try:
                        # Create join request in database
                        request_id = create_student_join_request(
                            class_id=class_data['id'],
                            student_name=st.session_state.get('first_name', 'Öğrenci'),
                            student_class=student_class
                        )
                        
                        # Store join request in session
                        st.session_state['join_request'] = {
                            'request_id': request_id,
                            'class_id': class_data['id'],
                            'class_name': class_data['class_name'],
                            'invite_code': class_data['invite_code'],
                            'student_name': st.session_state.get('first_name', 'Öğrenci'),
                            'student_class': student_class,
                            'status': 'pending',
                            'request_time': datetime.now().strftime("%H:%M")
                        }
                        st.success(f"Katılım isteğiniz gönderildi: {class_data['class_name']}")
                        st.info("Öğretmeninizin onayını bekleyiniz...")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                else:
                    st.error("Geçersiz davet kodu veya şifre.")

    # Show join request status
    if st.session_state.get('join_request'):
        request = st.session_state['join_request']
        
        if request['status'] == 'pending':
            st.warning(f"⏳ Katılım isteğiniz bekleniyor...")
            st.info(f"Sınıf: {request['class_name']} | İstek Zamanı: {request.get('request_time', 'Bilinmiyor')}")
            
            if st.button("🔄 Durumu Kontrol Et"):
                # Check actual status from database
                if 'request_id' in request:
                    db_status = get_request_status(request['request_id'])
                    if db_status and db_status != request['status']:
                        request['status'] = db_status
                        st.session_state['join_request'] = request
                        st.rerun()
                    else:
                        st.info("Durum değişikliği yok.")
                else:
                    st.rerun()
            
            if st.button("❌ İsteği İptal Et"):
                del st.session_state['join_request']
                st.info("Katılım isteğiniz iptal edildi.")
                st.rerun()
        
        elif request['status'] == 'approved':
            st.success(f"✅ Katılım isteğiniz onaylandı!")
            st.info(f"Sınıf: {request['class_name']}")
            
            if st.button("🎓 Sınıfa Gir"):
                st.session_state['in_student_classroom'] = True
                st.rerun()
        
        elif request['status'] == 'rejected':
            st.error(f"❌ Katılım isteğiniz reddedildi.")
            st.info(f"Sınıf: {request['class_name']}")
            
            if st.button("🔄 Yeni İstek Gönder"):
                del st.session_state['join_request']
                st.rerun()


    # Calendar and Class Management
    st.markdown("---")
    st.subheader("📅 Ders Takvimi ve Sınıf Yönetimi")
    
    # Calendar view
    st.subheader("Ders Takvimini Görüntüle")
    st.info("Onaylanan dersleriniz takvimde gösterilir. Dersler 📌 emojisi ile işaretlenir.")

    # Calendar navigation
    today = dt_date.today()
    if 'student_calendar_year' not in st.session_state:
        st.session_state['student_calendar_year'] = today.year
    if 'student_calendar_month' not in st.session_state:
        st.session_state['student_calendar_month'] = today.month

    year = st.session_state['student_calendar_year']
    month = st.session_state['student_calendar_month']

    # Calendar header with navigation
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️", help="Önceki yıl", key="student_prev_year"):
            st.session_state['student_calendar_year'] -= 1
            st.rerun()
    with col2:
        if st.button("◀️", help="Önceki ay", key="student_prev_month"):
            if st.session_state['student_calendar_month'] == 1:
                st.session_state['student_calendar_month'] = 12
                st.session_state['student_calendar_year'] -= 1
            else:
                st.session_state['student_calendar_month'] -= 1
            st.rerun()
    with col3:
        st.markdown(f"<h3 style='text-align: center; margin: 0;'>{py_calendar.month_name[month]} {year}</h3>", unsafe_allow_html=True)
    with col4:
        if st.button("▶️", help="Sonraki ay", key="student_next_month"):
            if st.session_state['student_calendar_month'] == 12:
                st.session_state['student_calendar_month'] = 1
                st.session_state['student_calendar_year'] += 1
            else:
                st.session_state['student_calendar_month'] += 1
            st.rerun()
    with col5:
        if st.button("⏭️", help="Sonraki yıl", key="student_next_year"):
            st.session_state['student_calendar_year'] += 1
            st.rerun()
    
    # Today button
    if st.button("📅 Bugüne Git", help="Bugünün tarihine dön", key="student_today"):
        st.session_state['student_calendar_year'] = today.year
        st.session_state['student_calendar_month'] = today.month
        st.rerun()

    # Get student's approved classes for the current month
    student_name = st.session_state.get('first_name', 'Öğrenci')
    approved_classes = get_student_approved_classes(student_name)
    
    # Group by date
    classes_by_date = {}
    
    for c in approved_classes:
        try:
            y, m, d = map(int, str(c['date']).split('-'))
            if y == year and m == month:
                classes_by_date.setdefault(d, []).append(c)
        except Exception:
            continue

    # Calendar grid
    week_days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    header_cols = st.columns(7)
    for idx, wd in enumerate(week_days):
        header_cols[idx].markdown(f"**{wd}**")

    for week in py_calendar.Calendar(firstweekday=0).monthdayscalendar(year, month):
        cols = st.columns(7)
        for i, day_num in enumerate(week):
            if day_num == 0:
                cols[i].markdown(" ")
                continue
            
            is_today = (year == today.year and month == today.month and day_num == today.day)
            has_class = day_num in classes_by_date
            
            if is_today and has_class:
                label = f"**{day_num}** 📌"
                cols[i].markdown(f'<span style="color: #2196f3; font-weight: bold;">{label}</span>', unsafe_allow_html=True)
            elif is_today:
                label = f"**{day_num}**"
                cols[i].markdown(f'<span style="color: #2196f3; font-weight: bold;">{label}</span>', unsafe_allow_html=True)
            elif has_class:
                label = f"{day_num} 📌"
                cols[i].markdown(label)
            else:
                cols[i].markdown(f"{day_num}")

    # Class Lists
    st.subheader("Ders Listesi")
    
    # Separate classes by past/future
    current_classes = []
    past_classes = []
    
    for c in approved_classes:
        try:
            class_date = datetime.strptime(c['date'], '%Y-%m-%d').date()
            class_time = datetime.strptime(c['time'], '%H:%M:%S').time()
            class_datetime = datetime.combine(class_date, class_time)
            now = datetime.now()
            
            if class_datetime < now:
                past_classes.append(c)
            else:
                current_classes.append(c)
        except Exception:
            current_classes.append(c)

    # Future classes
    st.subheader("Yaklaşan Dersler")
    if current_classes:
        for c in current_classes:
            st.markdown(f"- **{c['class_name']}** | {c['date']} {c['time']} | Davet Kodu: `{c['invite_code']}`")
            if c['description']:
                st.caption(f"   Açıklama: {c['description']}")
    else:
        st.info("Henüz yaklaşan dersiniz yok.")

    # Past classes
    st.subheader("Geçmiş Dersler")
    if past_classes:
        for c in past_classes:
            st.markdown(f"- **{c['class_name']}** | {c['date']} {c['time']} | Davet Kodu: `{c['invite_code']}`")
            if c['description']:
                st.caption(f"   Açıklama: {c['description']}")
    else:
        st.info("Henüz geçmiş dersiniz yok.")

    # Request History
    st.subheader("Katılım İstek Geçmişi")
    all_requests = get_student_requests(student_name)
    
    if all_requests:
        for req in all_requests:
            status_emoji = {
                'pending': '⏳',
                'approved': '✅',
                'rejected': '❌'
            }.get(req['status'], '❓')
            
            status_text = {
                'pending': 'Bekliyor',
                'approved': 'Onaylandı',
                'rejected': 'Reddedildi'
            }.get(req['status'], 'Bilinmiyor')
            
            st.markdown(f"{status_emoji} **{req['class_name']}** | {req['date']} {req['time']} | Durum: {status_text}")
            if req['description']:
                st.caption(f"   Açıklama: {req['description']}")
    else:
        st.info("Henüz katılım isteği göndermediniz.")
