import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import psycopg2

# Database connection string
conn_str = 'postgresql://postgres:jEicAaZs1btI16cN@immutably-incredible-dog.data-1.use1.tembo.io:5432/postgres'

# Connect to PostgreSQL database
def get_connection():
    return psycopg2.connect(conn_str)

st.title('📊 Sadhna Statistics')

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

c1, c2 = st.columns(2)

# Statistics
if not df.empty:
    with c1:
        current_date = datetime.now().date()
        start_of_week = current_date - timedelta(days=current_date.weekday())

        # Filter the dataframe for the current week
        current_week_data = df[df['date'].dt.date >= start_of_week]

        # Calculate the formatted week string for the current week
        current_week_str = f"W{start_of_week.isocalendar()[1]}-{start_of_week.year}"

        # Top 10 devotees for the current week
        top_10_weekly = current_week_data.groupby('devotee_name')['total_score'].sum().reset_index()
        top_10_weekly = top_10_weekly.sort_values(by='total_score', ascending=False).head(10)
        top_10_weekly['Formatted_Weekly'] = current_week_str

        st.write(f"🏅 Top 10 Devotees for the Current Week ({current_week_str})")
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
