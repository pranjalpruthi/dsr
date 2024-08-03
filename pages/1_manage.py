import streamlit as st
import psycopg2
import hmac

# Database connection string
conn_str = 'postgresql://postgres:jEicAaZs1btI16cN@immutably-incredible-dog.data-1.use1.tembo.io:5432/postgres'

# Connect to PostgreSQL database
def get_connection():
    return psycopg2.connect(conn_str)

# Password check function
def check_password():
    """Returns True if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

# ... (keep all your other functions like load_devotees, add_devotee, etc.)

# Streamlit app
st.set_page_config(
    page_title="Manage Devotees",
    page_icon="🙏",
    layout='wide',
)

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

st.title('Manage Devotees')

# Load devotees
devotees_list = load_devotees()
devotee_names = [devotee[1] for devotee in devotees_list]
devotee_ids = {devotee[1]: devotee[0] for devotee in devotees_list}

# ... (keep all your expander sections for adding, removing, renaming devotees, etc.)
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

# Sidebar options
with st.expander("Add Devotee"):
    new_devotee = st.text_input("New Devotee Name", key="new_devotee")
    if st.button("Add Devotee", key="add_devotee_button"):
        add_devotee(new_devotee)
        st.experimental_rerun()

with st.expander("Remove Devotee"):
    remove_devotee_name = st.selectbox("Select Devotee to Remove", devotee_names, key="remove_devotee")
    if st.button("Remove Devotee", key="remove_devotee_button"):
        remove_devotee(devotee_ids[remove_devotee_name])
        st.experimental_rerun()

with st.expander("Rename Devotee"):
    old_devotee_name = st.selectbox("Select Devotee to Rename", devotee_names, key="old_devotee")
    new_devotee_name = st.text_input("New Devotee Name", key="new_devotee_name")
    if st.button("Rename Devotee", key="rename_devotee_button"):
        rename_devotee(devotee_ids[old_devotee_name], new_devotee_name)
        st.experimental_rerun()

with st.expander("Show All Devotees"):
    st.write("List of all devotees:")
    for name in devotee_names:
        st.write(f"- {name}")

with st.expander("Remove Report"):
    report_id = st.number_input("Enter Report ID to Remove", min_value=1, step=1, key="report_id")
    if st.button("Remove Report", key="remove_report_button"):
        remove_report(report_id)
        st.experimental_rerun()

