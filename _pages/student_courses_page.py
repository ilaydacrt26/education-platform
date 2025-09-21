import streamlit as st
from utils.db import get_all_courses, get_teacher_name_by_id, get_quizzes_for_course, get_assignments_for_course, get_student_activity_status

def show():
    st.title("Öğrenci Ders Sayfası")
    st.write("Burada tüm dersleri görüntüleyebilirsiniz.")

    student_class = st.session_state.get('class') # Öğrencinin sınıfını session_state'ten al

    if not student_class:
        st.error("Öğrenci sınıf bilgisi bulunamadı. Lütfen giriş yapınız.")
        return

    # Veritabanından dersleri çek
    # get_all_courses fonksiyonu hem quizlerden hem de ödevlerden dersleri getirir.
    # target_class, course_name (teacher_branch olarak geçiyor)
    all_courses_data = get_all_courses(student_class) # Branch will be filtered in the loop if needed

    courses_display_data = {}
    for course in all_courses_data:
        course_name = course['course_name']
        teacher_id = course['teacher_id']
        
        if course_name not in courses_display_data:
            courses_display_data[course_name] = {
                "teachers": set(),
                "quizzes": [],
                "assignments": []
            }
        
        # Get teacher name
        teacher_info = get_teacher_name_by_id(teacher_id)
        if teacher_info:
            courses_display_data[course_name]["teachers"].add(f"{teacher_info['first_name']} {teacher_info['last_name']}")

    # Fetch quizzes and assignments for each course
    for course_name in courses_display_data.keys():
        quizzes = get_quizzes_for_course(course_name, student_class)
        if quizzes:
            courses_display_data[course_name]["quizzes"] = quizzes
        
        assignments = get_assignments_for_course(course_name, student_class)
        if assignments:
            courses_display_data[course_name]["assignments"] = assignments


    if courses_display_data:
        for course_name, data in courses_display_data.items():
            teachers_str = ", ".join(data["teachers"])
            with st.expander(f"{course_name}"):
                st.write(f"**Öğretmenler:** {teachers_str}")

                if data["quizzes"]:
                    st.subheader("Quizler")
                    for quiz in data["quizzes"]:
                        activity_status = get_student_activity_status(st.session_state.get('student_id'), 'quiz', quiz['id'])
                        status_text = activity_status['status']
                        if st.button(f"Quiz: {quiz['quiz_title']} (Durum: {status_text})", key=f"go_to_quiz_{quiz['id']}"):
                            st.session_state['page'] = 'student_quiz_page' # Yönlendirme
                            st.session_state['current_quiz_id'] = quiz['id']
                            st.rerun()
                else:
                    st.info(f"{course_name} dersine ait henüz quiz bulunmamaktadır.")

                if data["assignments"]:
                    st.subheader("Ödevler")
                    for assignment in data["assignments"]:
                        activity_status = get_student_activity_status(st.session_state.get('student_id'), 'assignment', assignment['id'])
                        status_text = activity_status['status']
                        if st.button(f"Ödev: {assignment['assignment_title']} (Durum: {status_text})", key=f"go_to_assignment_{assignment['id']}"):
                            st.session_state['page'] = 'student_assignment_page' # Yönlendirme
                            st.session_state['current_assignment_id'] = assignment['id']
                            st.rerun()
                else:
                    st.info(f"{course_name} dersine ait henüz ödev bulunmamaktadır.")

                # st.button("Derse Katıl", key=f"join_course_{course_name}") # Bu butona gerek kalmadı sanırım
    else:
        st.info(f"Henüz {student_class} sınıfına ait ders bulunmamaktadır.")
