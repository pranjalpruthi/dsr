import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import random

st.set_page_config(initial_sidebar_state="collapsed",
page_title="🪖 Daily Sadhana Report 📝 DSR v2.0",
page_icon="🪖 ",
layout='wide',)


# List of fixed devotees
devotees_list = [
    "Manu Dasa Prabhu", "Virkrishna das", "Eero-Taisto", "Amaury Prabhu", "Sreekanth", "Luveesh", "Varun prakash",
    "Krishnavinod Kutty", "Aditya Sharma", "Satyam Sharma", "Debalay Nandi", "Sami Saranpää", "Dmitriy/Dina Krishna Das Prabhu",
    "Ravi Singh", "Deepanshu Chaudhary", "Aryan Patney", "Gianni Prabhu", "Dharani Bharathi M", "Sai Karthi",
    "Drona Charan", "Vivek S", "Vivek Hk", "Vikas Prabhu", "Sujay Prabhu", "Pranjal Pruthi", "Pankaj Jalal",
    "Shivanshu Tewari", "Kallesh Prabhu", "Patita Pâvana dâsa", "Dama Ganga Sujith", "Bhakta Jad", "Sourav Sahoo",
    "Aditya Sree Kumar", "Mohith", "Pradheshwar Prabhu", "Privansh Prabhu", "Shivrani prabhu", "Subam Barman",
    "Veron Singh", "Arvindapada Krsna dasa", "Aryan", "Debalay Prabhu", "Drona Prabhu", "Ero-Taisto Prabhu", "Gianni Prabhu", "Krishna Vinod Prabhu",
    "Mohith Prabhu", "Patita Pavana dasa", "Shubam barman Prabhu"
]

# Function to calculate scores
def calculate_scores(df):
    df['Total Rounds'] = df['Before 7 am (Japa Session)'] + df['Before 7 am'] + df['7 to 09 am'] + df['After 9 am']
    df['Score (A)'] = (df['Before 7 am (Japa Session)'] * 2.5 + df['Before 7 am'] * 2 + df['7 to 09 am'] * 1.5 + df['After 9 am'] * 1).clip(upper=25)
    df['Score (B)'] = pd.cut(df['Book Reading Time Min'], bins=[-1, 1, 15, 30, 45, 60, float('inf')], labels=[0, 7, 15, 20, 25, 30], ordered=False).astype(int)
    df['Score (C)'] = pd.cut(df['Lecture Time Min'], bins=[-1, 15, 30, 45, float('inf')], labels=[7, 15, 20, 30], ordered=False).astype(int)
    df['Score (D)'] = pd.cut(df['Seva Time Min'], bins=[-1, 1, 15, 30, 45, 60, float('inf')], labels=[0, 5, 8, 12, 14, 15], ordered=False).astype(int)
    df['Total Score (A+B+C+D)'] = df['Score (A)'] + df['Score (B)'] + df['Score (C)'] + df['Score (D)']
    df['DATE'] = pd.to_datetime(df['DATE'])  # Ensure DATE column is in datetime format
    df['Monthly'] = df['DATE'].dt.to_period('M')
    df['Weekly'] = df['DATE'].dt.to_period('W')
    return df

# Streamlit app
st.title('🪖 Daily Sadhana Report 📝 DSR v0.0.3')

st.subheader('.💐Hare Kṛṣṇa Prabhus💐, Daṇḍavat Praṇāma🙇🏻‍♂️, Jaya Śrīla Prabhupāda! 🙌 ', divider='rainbow')

st.warning('🫡 Kindly fill this  📝 Hare Krishna DSR before ⏰12 Midnight 🌏Krishna Standard Time (KST).', icon="⚠️")

k1,k2 = st.columns(2)

with k1:
    # Form for input
    with st.form(key='sadhna_form'):
        st.header('📝 Fill Your Daily Sadhna Report 📿')
        
        # Date and Devotee Name
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input('📅 Date', value=datetime.today())
        with col2:
            devotee_name = st.selectbox('🙏 Devotee Name', devotees_list)
        
        # Japa Sessions
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            before_7am_japa = st.number_input('🌅 Before 7 am (Japa Session)', min_value=0, step=1)
        with col4:
            before_7am = st.number_input('🌄 Before 7 am', min_value=0, step=1)
        with col5:
            from_7_to_9am = st.number_input('🕖 7 to 09 am', min_value=0, step=1)
        with col6:
            after_9am = st.number_input('🌞 After 9 am', min_value=0, step=1)
        
        # Book Reading
        col7, col8 = st.columns(2)
        with col7:
            book_name = st.text_input('📚 Book Name')
        with col8:
            book_reading_time = st.number_input('📖 Book Reading Time Min', min_value=0, step=1)
        
        # Lecture
        col9, col10 = st.columns(2)
        with col9:
            lecture_speaker = st.text_input('🎤 Lecture Speaker')
        with col10:
            lecture_time = st.number_input('🕰️ Lecture Time Min', min_value=0, step=1)
        
        # Seva
        col11, col12 = st.columns(2)
        with col11:
            seva_name = st.text_input('🛠️ Seva Name')
        with col12:
            seva_time = st.number_input('⏳ Seva Time Min', min_value=0, step=1)
        
        submit_button = st.form_submit_button(label='✅ Hari Bol ! Jaya Śrīla Prabhupāda! 🙇🏻‍♂️ Submit', type="primary")


    # Initialize or load data
    if 'data' not in st.session_state:
        st.session_state['data'] = pd.DataFrame(columns=[
            'DATE', 'Devotee Name', 'Before 7 am (Japa Session)', 'Before 7 am', '7 to 09 am', 'After 9 am', 
            'Total Rounds', 'Score (A)', 'Book Name', 'Book Reading Time Min', 'Score (B)', 
            'Lecture Speaker', 'Lecture Time Min', 'Score (C)', 'Seva Name', 'Seva Time Min', 'Score (D)', 
            'Total Score (A+B+C+D)', 'Monthly', 'Weekly'
        ])

    # Add new entry to data
    if submit_button:
        new_entry = pd.DataFrame([{
            'DATE': date, 'Devotee Name': devotee_name, 'Before 7 am (Japa Session)': before_7am_japa, 
            'Before 7 am': before_7am, '7 to 09 am': from_7_to_9am, 'After 9 am': after_9am, 
            'Book Name': book_name, 'Book Reading Time Min': book_reading_time, 
            'Lecture Speaker': lecture_speaker, 'Lecture Time Min': lecture_time, 
            'Seva Name': seva_name, 'Seva Time Min': seva_time
        }])
        st.session_state['data'] = pd.concat([st.session_state['data'], new_entry], ignore_index=True)
        st.session_state['data'] = calculate_scores(st.session_state['data'])
with k2:

    # List of video URLs from your YouTube channel
    video_urls = [
    "https://youtube.com/watch?v=ll_rOl6oZbQ?si=t_EOYhp542llr3D4",
    "https://youtube.com/watch?v=yrx2YqyGs-E?si=AWqM94qUH8tyeh1H", 
    "https://youtube.com/watch?v=cgXjcaU2TOU?si=NtDwyihIR9gB-gVo", 
    "https://youtube.com/watch?v=SFrZd99l7gk?si=KgKodnT15zCumPPG", 
    "https://youtube.com/watch?v=9f-Aa-2fVqk?si=jJheFntrqEtkjBEh", 
        "https://youtu.be/O8nsZZ8Z-6g?si=YrHfuyupboqYBofX" ,
        "https://youtube.com/watch?v=yhWTbP1DAjA?si=Mp_JixZG8c4fCFzk",
        "https://youtu.be/0utP6oLxnT0?si=kEUTHiA78CUCOyx2",
        "https://youtu.be/fyBcO6ilyjw?si=MfYiezOlTZwSUn_4",
        "https://youtu.be/rmPLHbBbUzA?si=bJgrk6aIIe7CuR6p",
        "https://youtu.be/bZOlGRyknXM?si=70vbuytkjhKvN8fg",
        "https://youtu.be/PYtA10m_DBU?si=RyuduxsMf1oZ0FSQ"
        # Add more video URLs as needed
    ]

    # Select a random video URL
    random_video_url = random.choice(video_urls)

with k2:
    st.subheader('🪄📺')
    st.video(random_video_url)

#    with st.container():
 #       st.subheader('📺 Live Stream')
  #      for video_url in video_urls:
   #         st.video(video_url)

c1,c2 = st.columns(2)



# Statistics
if not st.session_state['data'].empty:

    with c1:

            # Top 10 devotees weekly
            top_10_weekly = st.session_state['data'].groupby(['Weekly', 'Devotee Name'])['Total Score (A+B+C+D)'].sum().reset_index()
            top_10_weekly = top_10_weekly.sort_values(by=['Weekly', 'Total Score (A+B+C+D)'], ascending=[True, False]).groupby('Weekly').head(10)
            st.write("🏅 Top 10 Devotees Weekly")
            st.dataframe(top_10_weekly)

            # Most favorite book of the week
            favorite_book_weekly = st.session_state['data'].groupby(['Weekly', 'Book Name'])['Book Name'].count().reset_index(name='count')
            favorite_book_weekly = favorite_book_weekly.sort_values(by=['Weekly', 'count'], ascending=[True, False]).groupby('Weekly').head(1)
            st.write("📚 Most Favorite Book of the Week")
            st.dataframe(favorite_book_weekly)

            # Devotee of the Week
            devotee_of_week = top_10_weekly.groupby('Weekly').first().reset_index()
            st.write("🌟 Devotee of the Week")
            st.dataframe(devotee_of_week[['Weekly', 'Devotee Name', 'Total Score (A+B+C+D)']])

    with c2:


            # Top 10 devotees monthly
            top_10_monthly = st.session_state['data'].groupby(['Monthly', 'Devotee Name'])['Total Score (A+B+C+D)'].sum().reset_index()
            top_10_monthly = top_10_monthly.sort_values(by=['Monthly', 'Total Score (A+B+C+D)'], ascending=[True, False]).groupby('Monthly').head(10)
            st.write("🏆 Top 10 Devotees Monthly")
            st.dataframe(top_10_monthly)


            # Devotee of the Month
            devotee_of_month = top_10_monthly.groupby('Monthly').first().reset_index()
            st.write("🌟 Devotee of the Month")
            st.dataframe(devotee_of_month[['Monthly', 'Devotee Name', 'Total Score (A+B+C+D)']])

            # Weekly intermediate devotees requiring spiritual guidance
            intermediate_devotees = st.session_state['data'].groupby(['Weekly', 'Devotee Name'])['Total Score (A+B+C+D)'].sum().reset_index()
            intermediate_devotees = intermediate_devotees[(intermediate_devotees['Total Score (A+B+C+D)'] > 0) & (intermediate_devotees['Total Score (A+B+C+D)'] < 50)]
            st.write("🧘‍♂️ Weekly Intermediate Devotees Requiring Spiritual Guidance")
            st.dataframe(intermediate_devotees)


    with c1:

        st.subheader('📊 Weekly Chart')

        # Weekly chart
        weekly_chart = st.session_state['data'].groupby(['Weekly', 'Devotee Name'])['Total Score (A+B+C+D)'].sum().reset_index()
        fig_weekly = px.bar(weekly_chart, x='Devotee Name', y='Total Score (A+B+C+D)', color='Weekly', title='Weekly Total Points per Devotee', barmode='stack')
        st.plotly_chart(fig_weekly)

    with c2:

        st.subheader('📊 Monthly Chart')

        # Monthly chart
        monthly_chart = st.session_state['data'].groupby(['Monthly', 'Devotee Name'])['Total Score (A+B+C+D)'].sum().reset_index()
        fig_monthly = px.bar(monthly_chart, x='Devotee Name', y='Total Score (A+B+C+D)', color='Monthly', title='Monthly Total Points per Devotee', barmode='stack')
        st.plotly_chart(fig_monthly)

# Display data
st.subheader('📊 Sadhna Data')
st.dataframe(st.session_state['data'])
