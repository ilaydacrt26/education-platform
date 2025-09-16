import streamlit as st

def show():
    st.title("Öğrenci Ders Sayfası")
    st.write("Burada tüm dersleri görüntüleyebilirsiniz.")

    st.subheader("Mevcut Dersler")

    # Placeholder for a list of courses
    courses = [
        {"title": "Matematik - Cebir", "teacher": "Öğretmen X", "description": "Cebir konularına giriş ve temel kavramlar."}, 
        {"title": "Türkçe - Edebiyat", "teacher": "Öğretmen Y", "description": "Divan Edebiyatı ve önemli şairler."}, 
        {"title": "Fen Bilimleri - Fizik", "teacher": "Öğretmen Z", "description": "Hareket ve Kuvvet konuları."}, 
    ]

    if courses:
        for i, course in enumerate(courses):
            with st.expander(f"{course['title']} ({course['teacher']})"):
                st.write(f"**Açıklama:** {course['description']}")
                st.button("Derse Katıl", key=f"join_course_{i}")
    else:
        st.info("Henüz mevcut ders bulunmamaktadır.")
