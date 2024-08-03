import streamlit as st
import psycopg2
import hmac
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Database connection string
conn_str = 'postgresql://postgres:jEicAaZs1btI16cN@immutably-incredible-dog.data-1.use1.tembo.io:5432/postgres'

# Connect to PostgreSQL database
def get_connection():
    return psycopg2.connect(conn_str)

# Load devotees list from database
def load_devotees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT devotee_id, devotee_name FROM devotees")
    devotees = cur.fetchall()
    cur.close()
    conn.close()
    return devotees

# Add devotee
def add_devotee(devotee_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO devotees (devotee_name) VALUES (%s) ON CONFLICT (devotee_name) DO NOTHING", (devotee_name,))
    conn.commit()
    cur.close()
    conn.close()

# Remove devotee
def remove_devotee(devotee_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM devotees WHERE devotee_id = %s", (devotee_id,))
    conn.commit()
    cur.close()
    conn.close()

# Rename devotee
def rename_devotee(devotee_id, new_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE devotees SET devotee_name = %s WHERE devotee_id = %s", (new_name, devotee_id))
    conn.commit()
    cur.close()
    conn.close()

# Remove report by ID
def remove_report(id):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM sadhna_report WHERE report_id = %s", (id,))
        conn.commit()
        st.success(f"Report with ID {id} has been removed successfully.")
    except psycopg2.Error as e:
        st.error(f"An error occurred while removing the report: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Load sadhana data
def load_sadhana_data():
    conn = get_connection()
    query = '''
    SELECT sr.*, d.devotee_name 
    FROM sadhna_report sr 
    JOIN devotees d ON sr.devotee_id = d.devotee_id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    return df

# Password check function
def check_password():
    """Returns True if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if "password" in st.secrets:
            entered_password = str(st.session_state["password"])
            correct_password = str(st.secrets["password"])
            if hmac.compare_digest(entered_password, correct_password):
                st.session_state["password_correct"] = True
                del st.session_state["password"]
            else:
                st.session_state["password_correct"] = False
        else:
            st.error("Password not set in app secrets.")
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

# Streamlit app
st.set_page_config(page_title="Manage Devotees", page_icon="🙏", layout='wide')

if not check_password():
    st.stop()

st.title('Manage Devotees')

# Load data
devotees_list = load_devotees()
devotee_names = [devotee[1] for devotee in devotees_list]
devotee_ids = {devotee[1]: devotee[0] for devotee in devotees_list}
df = load_sadhana_data()

# Sidebar options
with st.sidebar:
    st.header("Management Options")
    
    with st.expander("Add Devotee"):
        new_devotee = st.text_input("New Devotee Name", key="new_devotee")
        if st.button("Add Devotee", key="add_devotee_button"):
            add_devotee(new_devotee)
            st.rerun()

    with st.expander("Remove Devotee"):
        remove_devotee_name = st.selectbox("Select Devotee to Remove", devotee_names, key="remove_devotee")
        if st.button("Remove Devotee", key="remove_devotee_button"):
            remove_devotee(devotee_ids[remove_devotee_name])
            st.rerun()

    with st.expander("Rename Devotee"):
        old_devotee_name = st.selectbox("Select Devotee to Rename", devotee_names, key="old_devotee")
        new_devotee_name = st.text_input("New Devotee Name", key="new_devotee_name")
        if st.button("Rename Devotee", key="rename_devotee_button"):
            rename_devotee(devotee_ids[old_devotee_name], new_devotee_name)
            st.rerun()

    with st.expander("Remove Report"):
        report_id = st.number_input("Enter Report ID to Remove", min_value=1, step=1, key="report_id")
        if st.button("Remove Report", key="remove_report_button"):
            remove_report(report_id)
            st.rerun()

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Devotee Statistics")
    total_devotees = len(devotee_names)
    active_devotees = df['devotee_name'].nunique()
    st.metric("Total Devotees", total_devotees)
    st.metric("Active Devotees (Last 30 days)", active_devotees)

    st.subheader("Top 5 Most Active Devotees")
    top_devotees = df.groupby('devotee_name')['total_score'].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top_devotees)

with col2:
    st.subheader("Sadhana Report Statistics")
    total_reports = len(df)
    avg_score = df['total_score'].mean()
    st.metric("Total Reports", total_reports)
    st.metric("Average Score", f"{avg_score:.2f}")

    st.subheader("Reports per Day (Last 30 days)")
    last_30_days = df[df['date'] >= (datetime.now() - timedelta(days=30))]
    reports_per_day = last_30_days.groupby('date').size()
    st.line_chart(reports_per_day)

st.subheader("All Devotees")
st.dataframe(pd.DataFrame({"Devotee Name": devotee_names}))

st.subheader("Recent Sadhana Reports")
st.dataframe(df.sort_values('date', ascending=False).head(10))

st.subheader("Score Distribution")
fig = px.histogram(df, x="total_score", nbins=20, title="Distribution of Total Scores")
st.plotly_chart(fig)

st.subheader("Average Scores Over Time")
weekly_scores = df.groupby(df['date'].dt.to_period('W'))['total_score'].mean().reset_index()
weekly_scores['date'] = weekly_scores['date'].dt.to_timestamp()
fig = px.line(weekly_scores, x="date", y="total_score", title="Weekly Average Scores")
st.plotly_chart(fig)
