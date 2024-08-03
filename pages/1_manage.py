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
    try:
        cur.execute("INSERT INTO devotees (devotee_name) VALUES (%s) ON CONFLICT (devotee_name) DO NOTHING", (devotee_name,))
        conn.commit()
        return True, f"Devotee '{devotee_name}' added successfully."
    except psycopg2.Error as e:
        return False, f"Error adding devotee: {e}"
    finally:
        cur.close()
        conn.close()

# Remove devotee
def remove_devotee(devotee_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM devotees WHERE devotee_id = %s", (devotee_id,))
        conn.commit()
        return True, f"Devotee with ID {devotee_id} removed successfully."
    except psycopg2.Error as e:
        return False, f"Error removing devotee: {e}"
    finally:
        cur.close()
        conn.close()

# Rename devotee
def rename_devotee(devotee_id, new_name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE devotees SET devotee_name = %s WHERE devotee_id = %s", (new_name, devotee_id))
        conn.commit()
        return True, f"Devotee renamed to '{new_name}' successfully."
    except psycopg2.Error as e:
        return False, f"Error renaming devotee: {e}"
    finally:
        cur.close()
        conn.close()

# Remove report by ID
def remove_report(id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM sadhna_report WHERE report_id = %s", (id,))
        conn.commit()
        return True, f"Report with ID {id} removed successfully."
    except psycopg2.Error as e:
        return False, f"Error removing report: {e}"
    finally:
        cur.close()
        conn.close()

# Load reports from database
def load_reports():
    conn = get_connection()
    df = pd.read_sql_query('''
    SELECT sr.*, d.devotee_name 
    FROM sadhna_report sr 
    JOIN devotees d ON sr.devotee_id = d.devotee_id
    ''', conn)
    conn.close()
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
                del st.session_state["password"]  # Don't store the password.
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
    st.stop()  # Do not continue if check_password is not True.

st.title('Manage Devotees')

# Load data
devotees_list = load_devotees()
devotee_names = [devotee[1] for devotee in devotees_list]
devotee_ids = {devotee[1]: devotee[0] for devotee in devotees_list}
df = load_reports()

# Sidebar with metrics
st.sidebar.header("📊 Metrics")
total_devotees = len(devotee_names)
total_reports = len(df)
avg_score = df['total_score'].mean()

st.sidebar.metric("Total Devotees", total_devotees)
st.sidebar.metric("Total Reports", total_reports)
st.sidebar.metric("Average Score", f"{avg_score:.2f}")

# Main content
col1, col2 = st.columns(2)

with col1:
    with st.expander("➕ Add Devotee", expanded=True):
        new_devotee = st.text_input("New Devotee Name", key="new_devotee")
        if st.button("Add Devotee", key="add_devotee_button"):
            success, message = add_devotee(new_devotee)
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()

    with st.expander("🔄 Rename Devotee", expanded=True):
        old_devotee_name = st.selectbox("Select Devotee to Rename", devotee_names, key="old_devotee")
        new_devotee_name = st.text_input("New Devotee Name", key="new_devotee_name")
        if st.button("Rename Devotee", key="rename_devotee_button"):
            success, message = rename_devotee(devotee_ids[old_devotee_name], new_devotee_name)
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()

with col2:
    with st.expander("➖ Remove Devotee", expanded=True):
        remove_devotee_name = st.selectbox("Select Devotee to Remove", devotee_names, key="remove_devotee")
        if st.button("Remove Devotee", key="remove_devotee_button"):
            success, message = remove_devotee(devotee_ids[remove_devotee_name])
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()

    with st.expander("🗑️ Remove Report", expanded=True):
        report_id = st.number_input("Enter Report ID to Remove", min_value=1, step=1, key="report_id")
        if st.button("Remove Report", key="remove_report_button"):
            success, message = remove_report(report_id)
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()

# Charts
st.header("📈 Charts")

col3, col4 = st.columns(2)

with col3:
    # Top 10 devotees by total score
    top_10 = df.groupby('devotee_name')['total_score'].sum().nlargest(10).reset_index()
    fig1 = px.bar(top_10, x='devotee_name', y='total_score', title='Top 10 Devotees by Total Score')
    st.plotly_chart(fig1, use_container_width=True)

with col4:
    # Average score by month
    df['date'] = pd.to_datetime(df['date'])
    monthly_avg = df.groupby(df['date'].dt.to_period('M'))['total_score'].mean().reset_index()
    monthly_avg['date'] = monthly_avg['date'].dt.to_timestamp()
    fig2 = px.line(monthly_avg, x='date', y='total_score', title='Average Score by Month')
    st.plotly_chart(fig2, use_container_width=True)

# Show all devotees
with st.expander("👥 Show All Devotees", expanded=False):
    st.write("List of all devotees:")
    for name in devotee_names:
        st.write(f"- {name}")

# Recent reports
st.header("📋 Recent Reports")
recent_reports = df.sort_values('date', ascending=False).head(10)
st.dataframe(recent_reports, use_container_width=True)
