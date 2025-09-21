import streamlit as st
from utils.db import insert_quiz, insert_assignment # Import the new function
import os
import uuid # To generate unique filenames

def show():
    st.title("Öğretmen Ders Sayfası")
    st.write("Burada branşınıza göre dersleri yönetebilir, quizler ve ödevler oluşturabilirsiniz.")

    teacher_branch = st.session_state.get('branch', 'Belirtilmemiş') # Get teacher's branch from session state
    teacher_id = st.session_state.get('teacher_id') # Assuming teacher_id is stored in session state upon login

    # st.subheader(f"{teacher_branch} Dersleri")
    # st.info(f"Branşınız olan **{teacher_branch}** ile ilgili dersler burada listelenecektir.")

    st.subheader("Quiz Oluştur")
    
    # num_questions will be managed by the widget and reset by form_key_counter
    num_questions = st.number_input("Soru Sayısı", min_value=1, value=1, key="num_questions_input")

    with st.form(key="create_quiz_form"):
        quiz_title = st.text_input("Quiz Başlığı", key="quiz_title_input").strip()
        
        # Store questions and options dynamically
        questions_data = []
        for i in range(int(num_questions)):
            st.subheader(f"Soru {i+1}")
            question_text = st.text_area(f"Soru {i+1} Metni", key=f"question_text_{i}").strip()
            option_a = st.text_input(f"Soru {i+1} Seçenek A", key=f"option_a_{i}").strip()
            option_b = st.text_input(f"Soru {i+1} Seçenek B", key=f"option_b_{i}").strip()
            option_c = st.text_input(f"Soru {i+1} Seçenek C", key=f"option_c_{i}").strip()
            option_d = st.text_input(f"Soru {i+1} Seçenek D", key=f"option_d_{i}").strip()
            
            # Selectbox default value will be handled by the widget itself with the new form key
            correct_answer = st.selectbox(f"Soru {i+1} Doğru Cevap", ['A', 'B', 'C', 'D'], key=f"correct_answer_{i}")
            
            questions_data.append({
                "question_text": question_text,
                "option_a": option_a,
                "option_b": option_b,
                "option_c": option_c,
                "option_d": option_d,
                "correct_answer": correct_answer
            })
        
        classes = [str(i) for i in range(1, 13)] # Generate classes from 1 to 12 as numbers
        
        # Selected class default will be handled by the widget itself with the new form key
        selected_class = st.selectbox("Sınıf Seçimi", classes, key="selected_class_input")
        
        submit_button = st.form_submit_button(label='Quiz Oluştur')
        
        if submit_button:
            all_fields_filled = True
            if not teacher_id:
                st.error("Giriş yapınız.")
                all_fields_filled = False
            if not quiz_title.strip(): # Apply strip for validation
                st.error("Lütfen quiz başlığını giriniz.")
                all_fields_filled = False
            if not selected_class:
                st.error("Lütfen sınıf seçimi yapınız.")
                all_fields_filled = False
            if not teacher_branch:
                st.error("Öğretmen branşı bulunamadı.")
                all_fields_filled = False
            if not questions_data:
                st.error("Lütfen en az bir soru oluşturunuz.")
                all_fields_filled = False
            
            for i, q_data in enumerate(questions_data):
                if not q_data["question_text"].strip(): # Apply strip for validation
                    st.error(f"Soru {i+1} metni boş bırakılamaz.")
                    all_fields_filled = False
                if not q_data["option_a"].strip() or not q_data["option_b"].strip() or not q_data["option_c"].strip() or not q_data["option_d"].strip(): # Apply strip for validation
                    st.error(f"Soru {i+1} için tüm seçenekleri doldurunuz.")
                    all_fields_filled = False
            
            if all_fields_filled:
                insert_quiz(teacher_id, quiz_title.strip(), num_questions, selected_class, teacher_branch, questions_data)
                st.success(f"'{quiz_title.strip()}' başlıklı ve {num_questions} soruluk quiz, {selected_class} için oluşturuldu ve kaydedildi.")

    st.subheader("Ödev Oluştur ve Yükle")
    with st.form(key="create_assignment_form"):
        assignment_title = st.text_input("Ödev Başlığı", key="assignment_title_input").strip()
        assignment_description = st.text_area("Ödev Açıklaması", key="assignment_description_input").strip()
        assignment_due_date = st.date_input("Teslim Tarihi", key="assignment_due_date_input")
        
        uploaded_file = st.file_uploader("Ödev Dosyası Yükle", type=["pdf", "doc", "docx", "txt", "jpg", "jpeg", "png"], key="assignment_file_uploader")

        classes = [str(i) for i in range(1, 13)] # Generate classes from 1 to 12 as numbers
        selected_class_assignment = st.selectbox("Sınıf Seçimi", classes, key="selected_class_assignment_input")

        submit_assignment_button = st.form_submit_button(label='Ödev Oluştur')

        if submit_assignment_button:
            all_assignment_fields_filled = True
            assignment_file_path = None

            if not teacher_id:
                st.error("Giriş yapınız.")
                all_assignment_fields_filled = False
            if not assignment_title:
                st.error("Lütfen ödev başlığını giriniz.")
                all_assignment_fields_filled = False
            if not assignment_due_date:
                st.error("Lütfen teslim tarihi seçiniz.")
                all_assignment_fields_filled = False
            if not selected_class_assignment:
                st.error("Lütfen sınıf seçimi yapınız.")
                all_assignment_fields_filled = False
            if not teacher_branch:
                st.error("Öğretmen branşı bulunamadı.")
                all_assignment_fields_filled = False

            if uploaded_file is not None:
                # Create upload directory if it doesn't exist
                upload_dir = "./uploads/assignments"
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate a unique filename to prevent overwrites
                unique_filename = str(uuid.uuid4()) + os.path.splitext(uploaded_file.name)[1]
                assignment_file_path = os.path.join(upload_dir, unique_filename)
                
                with open(assignment_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            if all_assignment_fields_filled:
                insert_assignment(teacher_id, assignment_title, assignment_description, str(assignment_due_date), selected_class_assignment, teacher_branch, assignment_file_path)
                st.success(f"'{assignment_title}' başlıklı ödev, {selected_class_assignment} için oluşturuldu ve kaydedildi. Dosya yolu: {assignment_file_path if assignment_file_path else 'Yüklenmedi'}")
