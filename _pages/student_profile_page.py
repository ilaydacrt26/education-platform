import streamlit as st
import pandas as pd
from utils.db import get_student_comments
from datetime import datetime

def show():
    st.title("👤 Öğrenci Profil Sayfası")
    st.write("Burada kendi gelişiminizi, raporlarınızı ve öğretmen yorumlarınızı görüntüleyebilirsiniz.")
    
    # Öğrenci ID'sini session'dan al
    student_id = st.session_state.get('user_id')
    
    if not student_id:
        st.error("Öğrenci bilgileri bulunamadı. Lütfen tekrar giriş yapın.")
        return
    
    # Öğretmen yorumları bölümü
    st.subheader("💬 Öğretmen Yorumları")
    
    # Öğrencinin aldığı yorumları getir
    comments = get_student_comments(student_id)
    
    if comments:
        st.write(f"**{len(comments)} adet yorum bulundu:**")
        
        # Yorumları göster
        for i, comment in enumerate(comments):
            # SQL sorgusundaki sütun sırası:
            # 0: tc.id, 1: tc.comment_text, 2: tc.activity_type, 3: tc.activity_id, 
            # 4: tc.course_name, 5: tc.created_at, 6: t.first_name, 7: t.last_name, 8: activity_title
            with st.expander(f"📝 {comment[6]} {comment[7]} - {comment[8]}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Ders:** {comment[4]}")
                    st.write(f"**Aktivite:** {comment[8]} ({comment[2]})")
                    st.write(f"**Yorum:** {comment[1]}")
                
                with col2:
                    # Tarih formatını düzenle
                    try:
                        comment_date = datetime.strptime(comment[5], '%Y-%m-%d %H:%M:%S')
                        formatted_date = comment_date.strftime('%d.%m.%Y %H:%M')
                    except:
                        formatted_date = comment[5]
                    
                    st.write(f"**Tarih:** {formatted_date}")
                
                # Yorum ayırıcısı
                if i < len(comments) - 1:
                    st.divider()
    else:
        st.info("Henüz öğretmen yorumu bulunmuyor.")
    
    st.subheader("📊 Gelişim Grafiklerim")
    st.info("Derslere katılım, test skorları ve ödev tamamlama gibi gelişim grafikleriniz burada gösterilecektir.")

    st.subheader("📋 Raporlarım")
    st.info("Eğitim performansınıza dair detaylı raporlar burada listelenecektir.")
