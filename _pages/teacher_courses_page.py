import streamlit as st

def show():
    st.title("Öğretmen Ders Sayfası")
    st.write("Burada branşınıza göre dersleri yönetebilir ve ödev oluşturabilirsiniz.")

    teacher_branch = st.session_state.get('branch', 'Belirtilmemiş') # Get teacher's branch from session state

    st.subheader(f"{teacher_branch} Dersleri")
    st.info(f"Branşınız olan **{teacher_branch}** ile ilgili dersler burada listelenecektir.")

    st.subheader("Ödev Oluştur")
    with st.form(key='create_assignment_form'):
        assignment_title = st.text_input("Ödev Başlığı")
        assignment_description = st.text_area("Ödev Açıklaması")
        due_date = st.date_input("Teslim Tarihi")
        submit_button = st.form_submit_button(label='Ödev Oluştur')

        if submit_button:
            st.success(f"'{assignment_title}' başlıklı ödev oluşturuldu. Teslim Tarihi: {due_date}")
            # In a real application, this data would be saved to a database
