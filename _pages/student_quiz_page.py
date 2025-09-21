import streamlit as st
from utils.db import get_db_connection, get_student_activity_status, record_activity_start, record_activity_completion

def get_quiz_details(quiz_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    
    questions = []
    if quiz:
        cursor.execute("SELECT * FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
        questions = cursor.fetchall()
    conn.close()
    return quiz, questions

def show():
    st.title("Quiz Detayları ve Çözümü")

    student_id = st.session_state.get('student_id')
    current_quiz_id = st.session_state.get('current_quiz_id')

    if not student_id or not current_quiz_id:
        st.error("Quiz bilgilerine erişilemiyor. Lütfen dersler sayfasına geri dönün.")
        if st.button("Derslere Geri Dön"):
            st.session_state['page'] = 'student_courses_page'
            st.rerun()
        return
    
    quiz, questions = get_quiz_details(current_quiz_id)

    if not quiz:
        st.error("Quiz bulunamadı.")
        if st.button("Derslere Geri Dön"):
            st.session_state['page'] = 'student_courses_page'
            st.rerun()
        return

    st.subheader(f"Quiz: {quiz['quiz_title']}")
    st.info(f"Toplam Soru Sayısı: {quiz['num_questions']}")

    # Get student's activity status for this quiz
    activity_status = get_student_activity_status(student_id, 'quiz', current_quiz_id)
    status_text = activity_status['status']

    st.write(f"**Durum:** {status_text}")

    if status_text == 'Yapmadı':
        if st.button("Quize Başla", key="start_quiz_button"):
            record_activity_start(student_id, 'quiz', current_quiz_id)
            st.session_state['quiz_started'] = True
            st.rerun()
    elif status_text == 'Devam ediyor' or st.session_state.get('quiz_started'):
        st.write("Quiz devam ediyor...")

        user_answers = {}
        with st.form(key="quiz_form"):
            for i, question in enumerate(questions):
                st.markdown(f"**Soru {i+1}:** {question['question_text']}")
                options = {
                    'A': question['option_a'],
                    'B': question['option_b'],
                    'C': question['option_c'],
                    'D': question['option_d']
                }
                selected_option = st.radio(
                    f"Cevabınız",
                    list(options.keys()),
                    format_func=lambda x: f"{x}) {options[x]}",
                    key=f"question_{question['id']}"
                )
                user_answers[question['id']] = selected_option
            
            submit_quiz_button = st.form_submit_button(label="Quizi Bitir")

            if submit_quiz_button:
                correct_count = 0
                incorrect_count = 0
                for q_id, user_ans in user_answers.items():
                    # Find the question in the questions list to get the correct answer
                    q_obj = next((q for q in questions if q['id'] == q_id), None)
                    if q_obj and user_ans == q_obj['correct_answer']:
                        correct_count += 1
                    else:
                        incorrect_count += 1
                
                record_activity_completion(student_id, 'quiz', current_quiz_id, correct_answers=correct_count, incorrect_answers=incorrect_count)
                st.session_state['quiz_results'] = {
                    'correct': correct_count,
                    'incorrect': incorrect_count,
                    'total': quiz['num_questions']
                }
                st.session_state['quiz_started'] = False # Reset quiz started state
                st.rerun()
    elif status_text == 'Tamamladı':
        st.success("Bu quizi tamamladınız.")
        # Display results if available
        if activity_status['correct_answers'] is not None and activity_status['incorrect_answers'] is not None:
            st.write(f"**Doğru Cevap Sayısı:** {activity_status['correct_answers']}")
            st.write(f"**Yanlış Cevap Sayısı:** {activity_status['incorrect_answers']}")
        
        if st.button("Derslere Geri Dön", key="back_to_courses_from_completed_quiz"):
            st.session_state['page'] = 'student_courses_page'
            st.rerun()
