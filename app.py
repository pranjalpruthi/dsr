import streamlit as st
import pandas as pd
from datetime import datetime
import psycopg2
from psycopg2 import sql

# Database connection string
conn_str = 'postgresql://postgres:jEicAaZs1btI16cN@immutably-incredible-dog.data-1.use1.tembo.io:5432/postgres'

# Connect to PostgreSQL database
def get_connection():
    return psycopg2.connect(conn_str)

# Function to calculate scores
def calculate_scores(before_7_am_japa_session, before_7_am, from_7_to_9_am, after_9_am, book_reading_time_min, lecture_time_min, seva_time_min):
    total_rounds = before_7_am_japa_session + before_7_am + from_7_to_9_am + after_9_am
    score_a = min(before_7_am_japa_session * 2.5 + before_7_am * 2 + from_7_to_9_am * 1.5 + after_9_am * 1, 25)
    score_b = pd.cut([book_reading_time_min], bins=[-1, 1, 15, 30, 45, 60, float('inf')], labels=[0, 7, 15, 20, 30, 30], ordered=False).astype(int)[0].item()
    score_c = pd.cut([lecture_time_min], bins=[-1, 0, 15, 30, 45, float('inf')], labels=[0, 7, 15, 20, 30], ordered=False).astype(int)[0].item()
    score_d = pd.cut([seva_time_min], bins=[-1, 1, 15, 30, 45, 60, float('inf')], labels=[0, 5, 8, 12, 15, 15], ordered=False).astype(int)[0].item()
    total_score = score_a + score_b + score_c + score_d
    return total_rounds, score_a, score_b, score_c, score_d, total_score

# Load devotees list from database
def load_devotees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT devotee_id, devotee_name FROM devotees")
    devotees = cur.fetchall()
    cur.close()
    conn.close()
    return devotees

st.title('🪖 Daily Sadhana Report 📝 DSR v0.0.3')

# Load devotees
devotees_list = load_devotees()
devotee_names = [devotee[1] for devotee in devotees_list]
devotee_ids = {devotee[1]: devotee[0] for devotee in devotees_list}

# Form for input
k1, k2 = st.columns(2)
with k1:
    with st.form(key='sadhna_form'):
        st.header('📝 Fill Your Daily Sadhna Report 📿')
        
        # Date and Devotee Name
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input('📅 Date', value=datetime.today(), key="date_input")
        with col2:
            devotee_name = st.selectbox('🙏 Devotee Name', devotee_names, key="devotee_name_input")
        
        # Japa Sessions
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            before_7am_japa = st.number_input('🌅 Before 7 am (Japa Session)', min_value=0, step=1, key="before_7am_japa")
        with col4:
            before_7am = st.number_input('🌄 Before 7 am', min_value=0, step=1, key="before_7am")
        with col5:
            from_7_to_9am = st.number_input('🕖 7 to 09 am', min_value=0, step=1, key="from_7_to_9am")
        with col6:
            after_9am = st.number_input('🌞 After 9 am', min_value=0, step=1, key="after_9am")
        
        # Book Reading
        col7, col8 = st.columns(2)
        with col7:
            book_name = st.text_input('📚 Book Name', key="book_name")
        with col8:
            book_reading_time = st.number_input('📖 Book Reading Time Min', min_value=0, step=1, key="book_reading_time")
        
        # Lecture
        col9, col10 = st.columns(2)
        with col9:
            lecture_speaker = st.text_input('🎤 Lecture Speaker', key="lecture_speaker")
        with col10:
            lecture_time = st.number_input('🕰️ Lecture Time Min', min_value=0, step=1, key="lecture_time")
        
        # Seva
        col11, col12 = st.columns(2)
        with col11:
            seva_name = st.text_input('🛠️ Seva Name', key="seva_name")
        with col12:
            seva_time = st.number_input('⏳ Seva Time Min', min_value=0, step=1, key="seva_time")
        
        submit_button = st.form_submit_button(label='✅ Hari Bol ! Jaya Śrīla Prabhupāda! 🙇🏻‍♂️ Submit', type="primary")

    # Add new entry to database
    if submit_button:
        devotee_id = devotee_ids[devotee_name]
        total_rounds, score_a, score_b, score_c, score_d, total_score = calculate_scores(before_7am_japa, before_7am, from_7_to_9am, after_9am, book_reading_time, lecture_time, seva_time)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO sadhna_report (date, devotee_id, before_7_am_japa_session, before_7_am, from_7_to_9_am, after_9_am, book_name, book_reading_time_min, lecture_speaker, lecture_time_min, seva_name, seva_time_min, total_rounds, score_a, score_b, score_c, score_d, total_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (date, devotee_id, before_7am_japa, before_7am, from_7_to_9am, after_9am, book_name, book_reading_time, lecture_speaker, lecture_time, seva_name, seva_time, total_rounds, score_a, score_b, score_c, score_d, total_score))
        conn.commit()
        cur.close()
        conn.close()
        st.balloons()

with k2:
    # List of video URLs from your YouTube channel
    video_urls = [
        "https://youtube.com/watch?v=ll_rOl6oZbQ?si=t_EOYhp542llr3D4",
        "https://youtube.com/watch?v=yrx2YqyGs-E?si=AWqM94qUH8tyeh1H", 
        "https://youtube.com/watch?v=cgXjcaU2TOU?si=NtDwyihIR9gB-gVo", 
        "https://youtube.com/watch?v=SFrZd99l7gk?si=KgKodnT15zCumPPG", 
        "https://youtube.com/watch?v=9f-Aa-2fVqk?si=jJheFntrqEtkjBEh", 
        "https://youtu.be/O8nsZZ8Z-6g?si=YrHfuyupboqYBofX",
        "https://youtube.com/watch?v=yhWTbP1DAjA?si=Mp_JixZG8c4fCFzk",
        "https://youtu.be/0utP6oLxnT0?si=kEUTHiA78CUCOyx2",
        "https://youtu.be/fyBcO6ilyjw?si=MfYiezOlTZwSUn_4",
        "https://youtu.be/rmPLHbBbUzA?si=bJgrk6aIIe7CuR6p",
        "https://youtu.be/bZOlGRyknXM?si=70vbuytkjhKvN8fg",
        "https://youtu.be/PYtA10m_DBU?si=RyuduxsMf1oZ0FSQ"
    ]

    # Select a random video URL
    random_video_url = random.choice(video_urls)

    st.subheader('🪄📺')
    st.video(random_video_url)
