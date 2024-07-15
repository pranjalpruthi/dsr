import streamlit as st
import pandas as pd
from datetime import datetime

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
st.title('Daily Sadhna Report')

# Form for input
with st.form(key='sadhna_form'):
    date = st.date_input('Date', value=datetime.today())
    devotee_name = st.text_input('Devotee Name')
    before_7am_japa = st.number_input('Before 7 am (Japa Session)', min_value=0, step=1)
    before_7am = st.number_input('Before 7 am', min_value=0, step=1)
    from_7_to_9am = st.number_input('7 to 09 am', min_value=0, step=1)
    after_9am = st.number_input('After 9 am', min_value=0, step=1)
    book_name = st.text_input('Book Name')
    book_reading_time = st.number_input('Book Reading Time Min', min_value=0, step=1)
    lecture_speaker = st.text_input('Lecture Speaker')
    lecture_time = st.number_input('Lecture Time Min', min_value=0, step=1)
    seva_name = st.text_input('Seva Name')
    seva_time = st.number_input('Seva Time Min', min_value=0, step=1)
    submit_button = st.form_submit_button(label='Submit')

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

# Display data
st.dataframe(st.session_state['data'])
