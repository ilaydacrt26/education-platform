import streamlit as st

def show():
    st.title("Öğretmen Profil Sayfası")
    st.write("Burada öğrencilerinizin ilerlemesini görüntüleyebilirsiniz.")

    st.subheader("Öğrenci İlerlemesini Görüntüle")

    # Placeholder for selecting a student
    # In a real application, this would be populated from a database
    students = ["Öğrenci A", "Öğrenci B", "Öğrenci C"]
    selected_student = st.selectbox("Öğrenci Seçin", students)

    if selected_student:
        st.write(f"**{selected_student}** adlı öğrencinin ilerlemesi:")
        # Placeholder for student progress details
        st.info("Öğrencinin ders tamamlama oranı, test skorları ve ödev durumu burada gösterilecektir.")
