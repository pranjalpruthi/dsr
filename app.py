import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import random
import psycopg2
from psycopg2 import sql

# Database connection string
conn_str = 'postgresql://postgres:jEicAaZs1btI16cN@immutably-incredible-dog.data-1.use1.tembo.io:5432/postgres'

# Connect to PostgreSQL database
def get_connection():
    return psycopg2.connect(conn_str)

# Initialize PostgreSQL database
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS sadhna_report (
        DATE DATE,
        Devotee_Name TEXT UNIQUE,
        Before_7_am_Japa_Session INTEGER,
        Before_7_am INTEGER,
        From_7_to_9_am INTEGER,
        After_9_am INTEGER,
        Book_Name TEXT,
        Book_Reading_Time_Min INTEGER,
        Lecture_Speaker TEXT,
        Lecture_Time_Min INTEGER,
        Seva_Name TEXT,
        Seva_Time_Min INTEGER
    )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Function to calculate scores
def calculate_scores(df):
    df['Total Rounds'] = df['Before_7_am_Japa_Session'] + df['Before_7_am'] + df['From_7_to_9_am'] + df['After_9_am']
    df['Score (A)'] = (df['Before_7_am_Japa_Session'] * 2.5 + df['Before_7_am'] * 2 + df['From_7_to_9_am'] * 1.5 + df['After_9_am'] * 1).clip(upper=25)
    df['Score (B)'] = pd.cut(df['Book_Reading_Time_Min'], bins=[-1, 1, 15, 30, 45, 60, float('inf')], labels=[0, 7, 15, 20, 25, 30], ordered=False).astype(int)
    df['Score (C)'] = pd.cut(df['Lecture_Time_Min'], bins=[-1, 15, 30, 45, float('inf')], labels=[7, 15, 20, 30], ordered=False).astype(int)
    df['Score (D)'] = pd.cut(df['Seva_Time_Min'], bins=[-1, 1, 15, 30, 45, 60, float('inf')], labels=[0, 5, 8, 12, 14, 15], ordered=False).astype(int)
    df['Total Score (A+B+C+D)'] = df['Score (A)'] + df['Score (B)'] + df['Score (C)'] + df['Score (D)']
    df['DATE'] = pd.to_datetime(df['DATE'])  # Ensure DATE column is in datetime format
    df['Monthly'] = df['DATE'].dt.to_period('M')
    df['Weekly'] = df['DATE'].dt.to_period('W')
    df['Formatted_Weekly'] = df['Weekly'].apply(lambda x: f"W{x.week}-{x.year}")
    return df

# Initialize database
init_db()

# Streamlit app
st.set_page_config(
    page_title="🪖 Daily Sadhana Report 📝 DSR v0.0.3",
    page_icon="🪖 ",
    layout='wide',
)

st.title('🪖 Daily Sadhana Report 📝 DSR v0.0.3')

st.subheader('.💐Hare Kṛṣṇa Prabhus💐, Daṇḍavat Praṇāma🙇🏻‍♂️, Jaya Śrīla Prabhupāda! 🙌 ', divider='rainbow')

st.info('🫡 Kindly fill this  📝 Hare Krishna DSR before ⏰12 Midnight 🌏Krishna Standard Time (KST).', icon="⚠️")

# Sidebar for managing devotees
st.sidebar.header("Manage Devotees")

# Load devotees list from database
def load_devotees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT Devotee_Name FROM sadhna_report")
    devotees = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return devotees

# Add devotee
def add_devotee(devotee_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO sadhna_report (Devotee_Name) VALUES (%s)", (devotee_name,))
    conn.commit()
    cur.close()
    conn.close()

# Remove devotee
def remove_devotee(devotee_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sadhna_report WHERE Devotee_Name = %s", (devotee_name,))
    conn.commit()
    cur.close()
    conn.close()

# Rename devotee
def rename_devotee(old_name, new_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE sadhna_report SET Devotee_Name = %s WHERE Devotee_Name = %s", (new_name, old_name))
    conn.commit()
    cur.close()
    conn.close()

# Sidebar options
devotees_list = load_devotees()
with st.sidebar.expander("Add Devotee"):
    new_devotee = st.text_input("New Devotee Name", key="new_devotee")
    if st.button("Add Devotee", key="add_devotee_button"):
        add_devotee(new_devotee)
        st.experimental_rerun()

with st.sidebar.expander("Remove Devotee"):
    remove_devotee_name = st.selectbox("Select Devotee to Remove", devotees_list, key="remove_devotee")
    if st.button("Remove Devotee", key="remove_devotee_button"):
        remove_devotee(remove_devotee_name)
        st.experimental_rerun()

with st.sidebar.expander("Rename Devotee"):
    old_devotee_name = st.selectbox("Select Devotee to Rename", devotees_list, key="old_devotee")
    new_devotee_name = st.text_input("New Devotee Name", key="new_devotee_name")
    if st.button("Rename Devotee", key="rename_devotee_button"):
        rename_devotee(old_devotee_name, new_devotee_name)
        st.experimental_rerun()

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
            devotee_name = st.selectbox('🙏 Devotee Name', devotees_list, key="devotee_name_input")
        
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
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO sadhna_report (DATE, Devotee_Name, Before_7_am_Japa_Session, Before_7_am, From_7_to_9_am, After_9_am, Book_Name, Book_Reading_Time_Min, Lecture_Speaker, Lecture_Time_Min, Seva_Name, Seva_Time_Min)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (date, devotee_name, before_7am_japa, before_7am, from_7_to_9am, after_9am, book_name, book_reading_time, lecture_speaker, lecture_time, seva_name, seva_time))
        conn.commit()
        cur.close()
        conn.close()
        st.balloons()

# Load data from database
conn = get_connection()
df = pd.read_sql_query('SELECT * FROM sadhna_report', conn)
conn.close()

df = calculate_scores(df)

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

c1, c2 = st.columns(2)

# Statistics
if not df.empty:
    with c1:
        # Top 10 devotees weekly
        top_10_weekly = df.groupby(['Formatted_Weekly', 'Devotee_Name'])['Total Score (A+B+C+D)'].sum().reset_index()
        top_10_weekly = top_10_weekly.sort_values(by=['Formatted_Weekly', 'Total Score (A+B+C+D)'], ascending=[True, False]).groupby('Formatted_Weekly').head(10)
        st.write("🏅 Top 10 Devotees Weekly")
        st.dataframe(top_10_weekly, hide_index=True)

        # Most favorite book of the week
        favorite_book_weekly = df.groupby(['Formatted_Weekly', 'Book_Name'])['Book_Name'].count().reset_index(name='count')
        favorite_book_weekly = favorite_book_weekly.sort_values(by=['Formatted_Weekly', 'count'], ascending=[True, False]).groupby('Formatted_Weekly').head(1)
        st.write("📚 Most Favorite Book of the Week")
        st.dataframe(favorite_book_weekly, hide_index=True)

        # Devotee of the Week
        devotee_of_week = top_10_weekly.groupby('Formatted_Weekly').first().reset_index()
        st.write("🌟 Devotee of the Week")
        st.dataframe(devotee_of_week[['Formatted_Weekly', 'Devotee_Name', 'Total Score (A+B+C+D)']], hide_index=True)

    with c2:
        # Top 10 devotees monthly
        top_10_monthly = df.groupby(['Monthly', 'Devotee_Name'])['Total Score (A+B+C+D)'].sum().reset_index()
        top_10_monthly = top_10_monthly.sort_values(by=['Monthly', 'Total Score (A+B+C+D)'], ascending=[True, False]).groupby('Monthly').head(10)
        st.write("🏆 Top 10 Devotees Monthly")
        st.dataframe(top_10_monthly, hide_index=True)

        # Devotee of the Month
        devotee_of_month = top_10_monthly.groupby('Monthly').first().reset_index()
        st.write("🌟 Devotee of the Month")
        st.dataframe(devotee_of_month[['Monthly', 'Devotee_Name', 'Total Score (A+B+C+D)']], hide_index=True)

        # Weekly intermediate devotees requiring spiritual guidance
        intermediate_devotees = df.groupby(['Formatted_Weekly', 'Devotee_Name'])['Total Score (A+B+C+D)'].sum().reset_index()
        intermediate_devotees = intermediate_devotees[(intermediate_devotees['Total Score (A+B+C+D)'] > 0) & (intermediate_devotees['Total Score (A+B+C+D)'] < 50)]
        st.write("🧘‍♂️ Weekly Intermediate Devotees Requiring Spiritual Guidance")
        st.dataframe(intermediate_devotees, hide_index=True)

    with c1:
        st.subheader('🏅 Weekly Chart')

        # Weekly multi-select
        selected_weeks = st.multiselect('Select Weeks', options=df['Formatted_Weekly'].unique(), default=df['Formatted_Weekly'].unique(), key="weekly_multiselect")

        # Filter data based on selected weeks
        weekly_chart = df[df['Formatted_Weekly'].isin(selected_weeks)].groupby(['Formatted_Weekly', 'Devotee_Name'])['Total Score (A+B+C+D)'].sum().reset_index()
        fig_weekly = px.bar(weekly_chart, x='Devotee_Name', y='Total Score (A+B+C+D)', color='Formatted_Weekly', title='Weekly Total Points per Devotee', barmode='stack')
        st.plotly_chart(fig_weekly)

    with c2:
        st.subheader('🪖 Monthly Chart')

        # Monthly multi-select
        selected_months = st.multiselect('Select Months', options=df['Monthly'].unique(), default=df['Monthly'].unique(), key="monthly_multiselect")

        # Filter data based on selected months
        monthly_chart = df[df['Monthly'].isin(selected_months)].groupby(['Monthly', 'Devotee_Name'])['Total Score (A+B+C+D)'].sum().reset_index()
        fig_monthly = px.bar(monthly_chart, x='Devotee_Name', y='Total Score (A+B+C+D)', color='Monthly', title='Monthly Total Points per Devotee', barmode='stack')
        st.plotly_chart(fig_monthly)

# Display data
st.subheader('📊 Sadhna Data')
st.dataframe(df, hide_index=True)
