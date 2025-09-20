import streamlit as st
import calendar as py_calendar
from datetime import date as dt_date, datetime
from utils.db import create_virtual_class, list_virtual_classes_for_teacher, delete_virtual_class, create_event, list_events_for_teacher, delete_event, EVENT_TYPES

def show():
    st.title("Öğretmen Sanal Sınıf Modülü")
    st.write("Burada dersler oluşturabilir, takvimi yönetebilir ve takvime eklemeler yapabilirsiniz.")
    
    # Calendar and Class Management
    st.markdown("---")
    st.subheader("📅 Takvim ve Sınıf Yönetimi")
    
    # Calendar view
    st.subheader("Takvimi Görüntüle")
    st.info("Dersleriniz ve etkinlikleriniz takvimde gösterilir. Dersler 📌 emojisi ile işaretlenir.")

    # Calendar navigation
    today = dt_date.today()
    if 'calendar_year' not in st.session_state:
        st.session_state['calendar_year'] = today.year
    if 'calendar_month' not in st.session_state:
        st.session_state['calendar_month'] = today.month

    year = st.session_state['calendar_year']
    month = st.session_state['calendar_month']

    # Calendar header with navigation
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️", help="Önceki yıl", key="prev_year"):
            st.session_state['calendar_year'] -= 1
            st.rerun()
    with col2:
        if st.button("◀️", help="Önceki ay", key="prev_month"):
            if st.session_state['calendar_month'] == 1:
                st.session_state['calendar_month'] = 12
                st.session_state['calendar_year'] -= 1
            else:
                st.session_state['calendar_month'] -= 1
            st.rerun()
    with col3:
        st.markdown(f"<h3 style='text-align: center; margin: 0;'>{py_calendar.month_name[month]} {year}</h3>", unsafe_allow_html=True)
    with col4:
        if st.button("▶️", help="Sonraki ay", key="next_month"):
            if st.session_state['calendar_month'] == 12:
                st.session_state['calendar_month'] = 1
                st.session_state['calendar_year'] += 1
            else:
                st.session_state['calendar_month'] += 1
            st.rerun()
    with col5:
        if st.button("⏭️", help="Sonraki yıl", key="next_year"):
            st.session_state['calendar_year'] += 1
            st.rerun()
    
    # Today button
    if st.button("📅 Bugüne Git", help="Bugünün tarihine dön"):
        st.session_state['calendar_year'] = today.year
        st.session_state['calendar_month'] = today.month
        st.rerun()

    # Get classes and events for the current month
    classes = list_virtual_classes_for_teacher(
        teacher_first_name=st.session_state.get('first_name', 'Bilinmeyen'),
        teacher_last_name=st.session_state.get('last_name', ''),
    )
    events = list_events_for_teacher(
        teacher_first_name=st.session_state.get('first_name', 'Bilinmeyen'),
        teacher_last_name=st.session_state.get('last_name', ''),
    )
    
    # Group by date
    classes_by_date = {}
    events_by_date = {}
    
    for c in classes:
        try:
            y, m, d = map(int, str(c['date']).split('-'))
            if y == year and m == month:
                classes_by_date.setdefault(d, []).append(c)
        except Exception:
            continue
    
    for e in events:
        try:
            y, m, d = map(int, str(e['date']).split('-'))
            if y == year and m == month:
                events_by_date.setdefault(d, []).append(e)
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
            has_event = day_num in events_by_date
            
            emojis = []
            if has_class:
                emojis.append("📌")
            if has_event:
                for event in events_by_date.get(day_num, []):
                    emoji = EVENT_TYPES.get(event['event_type'], "📅")
                    if emoji not in emojis:
                        emojis.append(emoji)
            
            emoji_str = " ".join(emojis) if emojis else ""
            
            if is_today and (has_class or has_event):
                label = f"**{day_num}** {emoji_str}"
                cols[i].markdown(f'<span style="color: #2196f3; font-weight: bold;">{label}</span>', unsafe_allow_html=True)
            elif is_today:
                label = f"**{day_num}**"
                cols[i].markdown(f'<span style="color: #2196f3; font-weight: bold;">{label}</span>', unsafe_allow_html=True)
            elif has_class or has_event:
                label = f"{day_num} {emoji_str}"
                cols[i].markdown(label)
            else:
                cols[i].markdown(f"{day_num}")

    # Start virtual class
    st.subheader("Sanal Sınıfı Başlat")
    with st.form(key='start_virtual_class_form'):
        st.write("Mevcut bir sanal sınıfı başlatmak için davet kodunu ve şifreyi girin:")
        invite_code_input = st.text_input("Davet Kodu", placeholder="Örn: ABC12345")
        class_password_input = st.text_input("Sınıf Şifresi", type="password")
        start_class_button = st.form_submit_button(label='Sanal Sınıfı Başlat')
        
        if start_class_button:
            if not invite_code_input or not class_password_input:
                st.error("Lütfen davet kodunu ve şifreyi girin.")
            else:
                # Check if class exists and password is correct
                from utils.db import get_db_connection
                import bcrypt
                
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM virtual_classes 
                    WHERE invite_code = ? AND teacher_first_name = ? AND teacher_last_name = ?
                ''', (invite_code_input, 
                      st.session_state.get('first_name', 'Bilinmeyen'),
                      st.session_state.get('last_name', '')))
                
                class_data = cursor.fetchone()
                conn.close()
                
                if class_data and bcrypt.checkpw(class_password_input.encode('utf-8'), class_data['password'].encode('utf-8')):
                    st.session_state['active_class'] = {
                        'id': class_data['id'],
                        'name': class_data['class_name'],
                        'invite_code': class_data['invite_code'],
                        'description': class_data['description'],
                        'password': class_password_input  # Store the plain password for display
                    }
                    st.success(f"Sanal sınıf '{class_data['class_name']}' başlatıldı!")
                    st.rerun()
                else:
                    st.error("Geçersiz davet kodu veya şifre.")

    # Show active class controls
    if st.session_state.get('active_class'):
        active_class = st.session_state['active_class']
        st.success(f"🟢 Aktif Sınıf: {active_class['name']} (Kod: {active_class['invite_code']})")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎓 Sınıf Paneline Git"):
                st.session_state['in_classroom'] = True
                st.rerun()
        with col2:
            if st.button("Sınıfı Kapat"):
                del st.session_state['active_class']
                st.rerun()

    # Virtual Classroom Interface
    if st.session_state.get('in_classroom') and st.session_state.get('active_class'):
        st.markdown("---")
        st.subheader("🎓 Sanal Sınıf Ortamı")
        
        active_class = st.session_state['active_class']
        st.info(f"**Aktif Sınıf:** {active_class['name']} | **Davet Kodu:** {active_class['invite_code']}")
        
        # Teacher controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            camera_status = st.session_state.get('teacher_camera', False)
            if st.button("📹 Kamera", key="toggle_camera"):
                st.session_state['teacher_camera'] = not camera_status
                st.rerun()
            st.write("🟢 Açık" if camera_status else "🔴 Kapalı")
        
        with col2:
            mic_status = st.session_state.get('teacher_mic', False)
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
                del st.session_state['in_classroom']
                del st.session_state['active_class']
                st.rerun()
        
        # Virtual classroom content
        st.markdown("---")
        
        # Main video area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📹 Canlı Yayın")
            if st.session_state.get('teacher_camera', False):
                st.info("🎥 Kamera açık - Video yayını burada görünecek")
            else:
                st.warning("📹 Kamera kapalı")
            
            if st.session_state.get('teacher_screen', False):
                st.info("🖥️ Ekran paylaşımı aktif")
        
        with col2:
            st.subheader("👥 Katılımcılar")
            st.write("• Öğretmen (Siz)")
            # Real-time student list will be shown here
            if 'approved_students' in st.session_state and st.session_state['approved_students']:
                for student in st.session_state['approved_students']:
                    st.write(f"• {student['name']} ({student['class']})")
            else:
                st.write("• Henüz katılan öğrenci yok")
        
        # Chat section
        st.markdown("---")
        st.subheader("💬 Sınıf Sohbeti")
        
        # Initialize chat
        if 'classroom_chat' not in st.session_state:
            st.session_state['classroom_chat'] = []
        
        # Chat input
        chat_input = st.text_input("Mesajınızı yazın...", key="teacher_chat_input")
        if st.button("Gönder", key="send_teacher_message"):
            if chat_input:
                from datetime import datetime
                st.session_state['classroom_chat'].append({
                    'user': 'Öğretmen',
                    'message': chat_input,
                    'time': datetime.now().strftime("%H:%M")
                })
                st.rerun()
        
        # Display messages
        for msg in st.session_state['classroom_chat'][-5:]:
            st.write(f"**{msg['user']} ({msg['time']}):** {msg['message']}")
    
    # Show last created invite code
    if st.session_state.get('last_invite_code'):
        st.subheader("Son Oluşturulan Davet Kodu")
        st.text_input("Davet Kodu", st.session_state['last_invite_code'], key="last_invite_code_display", disabled=True)

    # Create new virtual class
    st.subheader("Yeni Sanal Sınıf Oluştur")
    with st.form(key='create_virtual_class_form'):
        class_name = st.text_input("Sınıf Adı")
        class_description = st.text_area("Sınıf Açıklaması")
        class_date = st.date_input("Ders Tarihi")
        class_time = st.time_input("Ders Saati")
        class_password = st.text_input("Sanal Sınıf Şifresi", type="password")
        create_class_button = st.form_submit_button(label='Sanal Sınıf Oluştur')

        if create_class_button:
            if not class_name or not class_password:
                st.error("Sınıf adı ve şifre zorunludur.")
            else:
                try:
                    invite_code = create_virtual_class(
                        teacher_first_name=st.session_state.get('first_name', 'Bilinmeyen'),
                        teacher_last_name=st.session_state.get('last_name', ''),
                        class_name=class_name,
                        description=class_description,
                        date_str=str(class_date),
                        time_str=str(class_time),
                        password_plain=class_password,
                    )
                    st.session_state['last_invite_code'] = invite_code
                    st.success(f"'{class_name}' adlı sanal sınıf oluşturuldu. Davet Kodu: {invite_code}")
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Sanal sınıf oluşturulurken hata oluştu: {e}")
    
    # Add event form
    st.subheader("Takvime Etkinlik Ekle")
    with st.form(key='add_event_to_calendar_form'):
        event_type = st.selectbox("Etkinlik Türü", list(EVENT_TYPES.keys()), help="Etkinlik türünü seçin")
        event_title = st.text_input("Etkinlik Başlığı", help="Etkinlik başlığını girin")
        event_description = st.text_area("Etkinlik Açıklaması")
        event_date = st.date_input("Etkinlik Tarihi")
        event_time = st.time_input("Etkinlik Saati")
        add_event_button = st.form_submit_button(label='Etkinliği Takvime Ekle')

        if add_event_button:
            if not event_title.strip():
                st.error("Lütfen geçerli bir etkinlik başlığı girin.")
            else:
                try:
                    success = create_event(
                        teacher_first_name=st.session_state.get('first_name', 'Bilinmeyen'),
                        teacher_last_name=st.session_state.get('last_name', ''),
                        title=event_title,
                        description=event_description,
                        date_str=str(event_date),
                        time_str=str(event_time),
                        event_type=event_type
                    )
                    if success:
                        st.success(f"'{event_title}' başlıklı etkinlik {event_date} tarihinde {event_time} saatinde takvime eklendi.")
                        st.rerun()
                    else:
                        st.error("Etkinlik eklenirken hata oluştu.")
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Etkinlik eklenirken hata oluştu: {e}")

    # Class and Event Lists
    st.subheader("Sınıf ve Etkinlik Listesi")
    
    # Separate classes by past/future
    current_classes = []
    past_classes = []
    
    for c in classes:
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
    st.subheader("Aktif Sanal Sınıflar")
    if current_classes:
        for c in current_classes:
            col_info, col_del = st.columns([5,1])
            with col_info:
                st.markdown(f"- {c['date']} {c['time']} | {c['class_name']} | Davet Kodu: `{c['invite_code']}`")
            with col_del:
                if st.button("Sil", key=f"del_class_{c['id']}"):
                    ok = delete_virtual_class(
                        class_id=c['id'],
                        teacher_first_name=st.session_state.get('first_name', 'Bilinmeyen'),
                        teacher_last_name=st.session_state.get('last_name', ''),
                    )
                    if ok:
                        st.success("Sanal sınıf silindi.")
                        st.rerun()
                    else:
                        st.error("Sanal sınıf silinemedi.")
    else:
        st.info("Henüz gelecekteki sanal sınıf oluşturmadınız.")

    # Separate events by past/future
    current_events = []
    past_events = []
    
    for e in events:
        try:
            event_date = datetime.strptime(e['date'], '%Y-%m-%d').date()
            event_time = datetime.strptime(e['time'], '%H:%M:%S').time()
            event_datetime = datetime.combine(event_date, event_time)
            now = datetime.now()
            
            if event_datetime < now:
                past_events.append(e)
            else:
                current_events.append(e)
        except Exception:
            current_events.append(e)

    # Future events
    st.subheader("Aktif Etkinlikler")
    if current_events:
        for e in current_events:
            emoji = EVENT_TYPES.get(e['event_type'], "📅")
            col_info, col_del = st.columns([5,1])
            with col_info:
                st.markdown(f"- {e['date']} {e['time']} | {emoji} {e['title']} ({e['event_type']})")
            with col_del:
                if st.button("Sil", key=f"del_event_{e['id']}"):
                    ok = delete_event(
                        event_id=e['id'],
                        teacher_first_name=st.session_state.get('first_name', 'Bilinmeyen'),
                        teacher_last_name=st.session_state.get('last_name', ''),
                    )
                    if ok:
                        st.success("Etkinlik silindi.")
                        st.rerun()
                    else:
                        st.error("Etkinlik silinemedi.")
    else:
        st.info("Henüz gelecekteki etkinlik oluşturmadınız.")

    # Past classes
    st.subheader("Geçmiş Sanal Sınıflar")
    if past_classes:
        for c in past_classes:
            col_info, col_del = st.columns([5,1])
            with col_info:
                st.markdown(f"- {c['date']} {c['time']} | {c['class_name']} | Davet Kodu: `{c['invite_code']}`")
            with col_del:
                if st.button("Sil", key=f"del_past_class_{c['id']}"):
                    ok = delete_virtual_class(
                        class_id=c['id'],
                        teacher_first_name=st.session_state.get('first_name', 'Bilinmeyen'),
                        teacher_last_name=st.session_state.get('last_name', ''),
                    )
                    if ok:
                        st.success("Sanal sınıf silindi.")
                        st.rerun()
                    else:
                        st.error("Sanal sınıf silinemedi.")
    else:
        st.info("Henüz geçmiş sanal sınıf yok.")
        
    # Past events
    st.subheader("Geçmiş Etkinlikler")
    if past_events:
        for e in past_events:
            emoji = EVENT_TYPES.get(e['event_type'], "📅")
            col_info, col_del = st.columns([5,1])
            with col_info:
                st.markdown(f"- {e['date']} {e['time']} | {emoji} {e['title']} ({e['event_type']})")
            with col_del:
                if st.button("Sil", key=f"del_past_event_{e['id']}"):
                    ok = delete_event(
                        event_id=e['id'],
                        teacher_first_name=st.session_state.get('first_name', 'Bilinmeyen'),
                        teacher_last_name=st.session_state.get('last_name', ''),
                    )
                    if ok:
                        st.success("Etkinlik silindi.")
                        st.rerun()
                    else:
                        st.error("Etkinlik silinemedi.")
    else:
        st.info("Henüz geçmiş etkinlik yok.")
