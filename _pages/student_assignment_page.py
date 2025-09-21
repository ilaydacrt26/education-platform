import streamlit as st
from utils.db import get_db_connection, get_student_activity_status, record_activity_start, record_activity_completion
import os
import uuid # For unique filenames

def get_assignment_details(assignment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,))
    assignment = cursor.fetchone()
    conn.close()
    return assignment

def show():
    st.title("Ödev Detayları ve Teslimi")

    student_id = st.session_state.get('student_id')
    current_assignment_id = st.session_state.get('current_assignment_id')

    if not student_id or not current_assignment_id:
        st.error("Ödev bilgilerine erişilemiyor. Lütfen dersler sayfasına geri dönün.")
        if st.button("Derslere Geri Dön"):
            st.session_state['page'] = 'student_courses_page'
            st.rerun()
        return
    
    assignment = get_assignment_details(current_assignment_id)

    if not assignment:
        st.error("Ödev bulunamadı.")
        if st.button("Derslere Geri Dön"):
            st.session_state['page'] = 'student_courses_page'
            st.rerun()
        return

    st.subheader(f"Ödev: {assignment['assignment_title']}")
    st.write(f"**Açıklama:** {assignment['description']}")
    st.write(f"**Teslim Tarihi:** {assignment['due_date']}")
    
    if assignment['file_path']:
        file_path = assignment['file_path']
        file_name = os.path.basename(file_path)
        try:
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Öğretmen Dosyasını İndir",
                    data=f.read(),
                    file_name=file_name,
                    mime="application/octet-stream" # Generic MIME type for downloads
                )
        except FileNotFoundError:
            st.error("Öğretmen dosyası bulunamadı.")
    
    # Get student's activity status for this assignment
    activity_status = get_student_activity_status(student_id, 'assignment', current_assignment_id)
    status_text = activity_status['status']
    submission_data = activity_status['submission_data']

    st.write(f"**Durum:** {status_text}")

    if status_text == 'Yapmadı':
        if st.button("Ödeve Başla", key="start_assignment_button"):
            record_activity_start(student_id, 'assignment', current_assignment_id)
            st.session_state['assignment_started'] = True
            st.rerun()
    elif status_text == 'Devam ediyor' or st.session_state.get('assignment_started'):
        st.write("Ödev devam ediyor...")

        with st.form(key="assignment_submission_form"):
            st.markdown("**Ödev Teslimi**")
            student_text_answer = st.text_area("Cevabınızı buraya yazın (isteğe bağlı)", key="student_assignment_text_answer")
            student_uploaded_file = st.file_uploader("Veya dosya yükleyin (isteğe bağlı)", type=["pdf", "doc", "docx", "txt", "jpg", "jpeg", "png"], key="student_assignment_file_uploader")
            
            submit_assignment_button = st.form_submit_button(label="Ödevi Gönder")

            if submit_assignment_button:
                submitted_file_path = None
                if student_uploaded_file is not None:
                    # Create upload directory if it doesn't exist
                    upload_dir = "./uploads/submissions"
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generate a unique filename to prevent overwrites
                    unique_filename = f"student_{student_id}_assignment_{current_assignment_id}_" + str(uuid.uuid4()) + os.path.splitext(student_uploaded_file.name)[1]
                    submitted_file_path = os.path.join(upload_dir, unique_filename)
                    
                    with open(submitted_file_path, "wb") as f:
                        f.write(student_uploaded_file.getbuffer())
                
                # Determine submission data (text or file path)
                final_submission_data = student_text_answer if student_text_answer else submitted_file_path

                record_activity_completion(student_id, 'assignment', current_assignment_id, submission_data=final_submission_data)
                st.success("Ödeviniz başarıyla gönderildi!")
                st.session_state['assignment_started'] = False # Reset state
                st.rerun()
    elif status_text == 'Tamamladı':
        st.success("Bu ödevi tamamladınız.")
        if submission_data:
            st.write(f"**Gönderdiğiniz Cevap/Dosya:** {submission_data}")
        
        if st.button("Derslere Geri Dön", key="back_to_courses_from_completed_assignment"):
            st.session_state['page'] = 'student_courses_page'
            st.rerun()
