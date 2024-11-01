import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import random
import psycopg2
from psycopg2 import sql
import streamlit_shadcn_ui as ui

# Database connection string
conn_str = 'postgresql://postgres:iQfQoY5xqjtDpUlo@finely-wealthy-rudderfish.data-1.apse1.tembo.io:5432/postgres'

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

# Streamlit app
st.set_page_config(
    page_title="🪖 Daily Sadhana Report 📝 ",
    page_icon="🪖 ",
    layout='wide',
)

# Title with version badge
st.title('🪖 Daily Sadhana Report')

# Display version badge
ui.badges(
    badge_list=[("v0.0.4 - 🌼 Govardhan Lifter Stage 🌼 [mataji-edition]", "default")],
    class_name="flex gap-2",
    key="version_badge"
)

# Load data from database
conn = get_connection()
df = pd.read_sql_query('''
SELECT sr.*, d.devotee_name 
FROM sadhna_report sr 
JOIN devotees d ON sr.devotee_id = d.devotee_id
''', conn)
conn.close()

# Ensure date column is in datetime format
df['date'] = pd.to_datetime(df['date'])

# Calculate weekly and monthly periods
df['Monthly'] = df['date'].dt.to_period('M')
df['Weekly'] = df['date'].dt.to_period('W')
df['Formatted_Weekly'] = df['Weekly'].apply(lambda x: f"W{x.week}-{x.year}")

# Load devotees list from database
def load_devotees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT devotee_id, devotee_name FROM devotees")
    devotees = cur.fetchall()
    cur.close()
    conn.close()
    return devotees

# Load devotees
devotees_list = load_devotees()
devotee_names = [devotee[1] for devotee in devotees_list]
devotee_ids = {devotee[1]: devotee[0] for devotee in devotees_list}

# Calculate metrics
current_date = datetime.now().date()
start_of_week = current_date - timedelta(days=current_date.weekday())
current_week_data = df[df['date'].dt.date >= start_of_week]
num_reports_this_week = current_week_data.shape[0]
total_devotees = len(devotee_names)
intermediate_devotees = df.groupby(['Formatted_Weekly', 'devotee_name'])['total_score'].sum().reset_index()
intermediate_devotees = intermediate_devotees[(intermediate_devotees['total_score'] > 0) & (intermediate_devotees['total_score'] < 50)]
num_intermediate_devotees = intermediate_devotees.shape[0]

# Display metrics using metric cards
cols = st.columns(3)
with cols[0]:
    ui.metric_card(title="📅 Reports This Week", content=f"{num_reports_this_week}", description="Number of reports submitted this week", key="reports_this_week")
with cols[1]:
    ui.metric_card(title="🙏 Total Devotees", content=f"{total_devotees}", description="Total number of devotees", key="total_devotees")
with cols[2]:
    ui.metric_card(title="🧘‍♂️ Devotees Requiring Attention", content=f"{num_intermediate_devotees}", description="Devotees requiring spiritual guidance", key="devotees_attention")

st.subheader('💐Hare Kṛṣṇa Matajis, Daṇḍavat Praṇāma🙇🏻‍♂️, Jaya Śrīla Prabhupāda! 🙌 ', divider='rainbow')

st.info('🫡 Kindly fill this  📝 Hare Krishna DSR before ⏰12 Midnight 🌏Krishna Standard Time (KST).', icon="⚠️")

# Link to manage devotees page
st.sidebar.header("Navigation")
st.sidebar.markdown("[Manage Devotees](2_manage.py)")

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

# Load data from database
conn = get_connection()
df = pd.read_sql_query('''
SELECT sr.*, d.devotee_name 
FROM sadhna_report sr 
JOIN devotees d ON sr.devotee_id = d.devotee_id
''', conn)
conn.close()

# Ensure date column is in datetime format
df['date'] = pd.to_datetime(df['date'])

# Calculate weekly and monthly periods
df['Monthly'] = df['date'].dt.to_period('M')
df['Weekly'] = df['date'].dt.to_period('W')
df['Formatted_Weekly'] = df['Weekly'].apply(lambda x: f"W{x.week}-{x.year}")

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
        # Get unique weeks
        unique_weeks = df['Formatted_Weekly'].unique()
        current_week_str = f"W{start_of_week.isocalendar()[1]}-{start_of_week.year}"

        # Select week
        selected_week = st.selectbox('Select Week', options=unique_weeks, index=list(unique_weeks).index(current_week_str))

        # Filter data for the selected week
        selected_week_data = df[df['Formatted_Weekly'] == selected_week]

        # Top 10 devotees for the selected week
        top_10_weekly = selected_week_data.groupby('devotee_name')['total_score'].sum().reset_index()
        top_10_weekly = top_10_weekly.sort_values(by='total_score', ascending=False).head(10)
        top_10_weekly['Formatted_Weekly'] = selected_week

        st.write(f"🏅 Top 10 Devotees for the Week ({selected_week})")
        st.dataframe(top_10_weekly[['Formatted_Weekly', 'devotee_name', 'total_score']], hide_index=True)

        # Most favorite book of the week
        favorite_book_weekly = df.groupby(['Formatted_Weekly', 'book_name'])['book_name'].count().reset_index(name='count')
        favorite_book_weekly = favorite_book_weekly.sort_values(by=['Formatted_Weekly', 'count'], ascending=[True, False]).groupby('Formatted_Weekly').head(1)
        st.write("📚 Most Favorite Book of the Week")
        st.dataframe(favorite_book_weekly, hide_index=True)

        # Devotee of the Week
        devotee_of_week = top_10_weekly.groupby('Formatted_Weekly').first().reset_index()
        st.write("🌟 Devotee of the Week")
        st.dataframe(devotee_of_week[['Formatted_Weekly', 'devotee_name', 'total_score']], hide_index=True)

    with c2:
        current_month = datetime.now().strftime('%B')
        current_year = datetime.now().year

        # Filter the dataframe for the current month
        current_month_data = df[df['date'].dt.to_period('M') == pd.Period(f"{current_year}-{datetime.now().month}")]

        # Top 10 devotees for the current month
        top_10_monthly = current_month_data.groupby('devotee_name')['total_score'].sum().reset_index()
        top_10_monthly = top_10_monthly.sort_values(by='total_score', ascending=False).head(10)
        top_10_monthly['Month'] = f"{current_month} {current_year}"

        st.write(f"🏆 Top 10 Devotees for {current_month} {current_year}")
        st.dataframe(top_10_monthly[['Month', 'devotee_name', 'total_score']], hide_index=True)

        # Devotee of the Month
        if not top_10_monthly.empty:
            devotee_of_month = top_10_monthly.iloc[0]
            st.write(f"🌟 Devotee of the Month ({current_month} {current_year})")
            st.dataframe(pd.DataFrame({
                'Month': [devotee_of_month['Month']],
                'devotee_name': [devotee_of_month['devotee_name']],
                'total_score': [devotee_of_month['total_score']]
            }), hide_index=True)

        # Weekly intermediate devotees requiring spiritual guidance
        intermediate_devotees = df.groupby(['Formatted_Weekly', 'devotee_name'])['total_score'].sum().reset_index()
        intermediate_devotees = intermediate_devotees[(intermediate_devotees['total_score'] > 0) & (intermediate_devotees['total_score'] < 50)]
        st.write("🧘‍♂️ Weekly Intermediate Devotees Requiring Spiritual Guidance")
        st.dataframe(intermediate_devotees, hide_index=True)

    with c1:
        st.subheader('🏅 Weekly Chart')

        # Weekly multi-select
        weekly_options = df['Formatted_Weekly'].unique()
        default_weekly = [week for week in weekly_options if week in weekly_options]

        selected_weeks = st.multiselect('Select Weeks', options=weekly_options, default=default_weekly, key="weekly_multiselect")

        # Filter data based on selected weeks
        weekly_chart = df[df['Formatted_Weekly'].isin(selected_weeks)].groupby(['Formatted_Weekly', 'devotee_name'])['total_score'].sum().reset_index()
        fig_weekly = px.bar(weekly_chart, x='devotee_name', y='total_score', color='Formatted_Weekly', title='Weekly Total Points per Devotee', barmode='stack')
        st.plotly_chart(fig_weekly)

    with c2:
        st.subheader('🪖 Monthly Chart')

        # Monthly multi-select
        monthly_options = df['Monthly'].unique()
        default_monthly = [month for month in monthly_options if month in monthly_options]

        selected_months = st.multiselect('Select Months', options=monthly_options, default=default_monthly, key="monthly_multiselect")

        # Filter data based on selected months
        monthly_chart = df[df['Monthly'].isin(selected_months)].groupby(['Monthly', 'devotee_name'])['total_score'].sum().reset_index()
        fig_monthly = px.bar(monthly_chart, x='devotee_name', y='total_score', color='Monthly', title='Monthly Total Points per Devotee', barmode='stack')
        st.plotly_chart(fig_monthly)


desired_order = [
    'date', 'report_id', 'devotee_name', 'devotee_id', 'total_score',
    'before_7_am_japa_session', 'before_7_am', 'from_7_to_9_am', 'after_9_am',
    'total_rounds', 'score_a', 'book_name', 'book_reading_time_min', 'score_b',
    'lecture_speaker', 'lecture_time_min', 'score_c', 'seva_name', 'seva_time_min',
    'score_d', 'Monthly', 'Weekly', 'Formatted_Weekly'
]

# Reorder the columns
df = df.reindex(columns=desired_order)

# Format the date column to show only the date part
df['date'] = df['date'].dt.date


# Display data
st.subheader('📊 Sadhna Data')
st.dataframe(df, hide_index=True)
