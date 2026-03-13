import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from ego import MarksManager

# Initialize database
@st.cache_resource
def get_db():
    return MarksManager()

db = get_db()

st.set_page_config(page_title="Student Marks Recorder", layout="wide")
st.title("📊 Student Marks Recorder & Visualizer")

# Sidebar navigation
menu = st.sidebar.radio("Menu", ["View Records", "Add Record", "Statistics", "Visualizations"])

if menu == "View Records":
    st.header("All Records")
    df = db.get_all_records()
    if not df.empty:
        # Editable dataframe? Streamlit has experimental data editor.
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        # Detect changes? For simplicity, we'll just display.
        # We could add delete/update via additional buttons.
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Delete Selected"):
                # In data_editor, we can get selected rows via st.session_state?
                # Simpler: Use selectbox to delete by ID
                pass
    else:
        st.info("No records yet.")

elif menu == "Add Record":
    st.header("Add New Record")
    with st.form("add_form"):
        name = st.text_input("Student Name")
        subject = st.text_input("Subject")
        marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=0.5)
        submitted = st.form_submit_button("Add")
        if submitted:
            if name and subject:
                db.add_record(name, subject, marks)
                st.success("Record added!")
                st.rerun()
            else:
                st.error("Name and Subject required.")

elif menu == "Statistics":
    st.header("Statistics")
    df = db.get_all_records()
    if not df.empty:
        subjects = ["All"] + list(df['subject'].unique())
        selected_subject = st.selectbox("Filter by subject", subjects)
        if selected_subject == "All":
            stats = db.get_statistics()
            filtered_df = df
        else:
            stats = db.get_statistics(selected_subject)
            filtered_df = df[df['subject'] == selected_subject]
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Count", stats['count'])
            col2.metric("Average", f"{stats['average']:.2f}")
            col3.metric("Median", f"{stats['median']:.2f}")
            col4.metric("Std Dev", f"{stats['std']:.2f}")
            col1.metric("Max", stats['max'])
            col2.metric("Min", stats['min'])
        else:
            st.warning("No data for this subject.")
    else:
        st.info("No data available.")

elif menu == "Visualizations":
    st.header("Visualizations")
    df = db.get_all_records()
    if df.empty:
        st.warning("No data to visualize.")
    else:
        viz_type = st.selectbox("Select Chart", 
                                ["Bar Chart (Avg per Student)", 
                                 "Histogram", 
                                 "Subject Comparison (Box Plot)",
                                 "Pass/Fail Pie"])
        
        if viz_type == "Bar Chart (Avg per Student)":
            avg_df = df.groupby('name')['marks'].mean().reset_index()
            fig, ax = plt.subplots()
            ax.bar(avg_df['name'], avg_df['marks'])
            ax.set_title("Average Marks per Student")
            ax.set_xlabel("Student")
            ax.set_ylabel("Average Marks")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        elif viz_type == "Histogram":
            fig, ax = plt.subplots()
            ax.hist(df['marks'], bins=10, edgecolor='black')
            ax.set_title("Distribution of Marks")
            ax.set_xlabel("Marks")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
        
        elif viz_type == "Subject Comparison (Box Plot)":
            fig, ax = plt.subplots()
            df.boxplot(column='marks', by='subject', ax=ax)
            ax.set_title("Marks by Subject")
            ax.set_xlabel("Subject")
            ax.set_ylabel("Marks")
            plt.suptitle("")  # Remove default suptitle
            st.pyplot(fig)
        
        elif viz_type == "Pass/Fail Pie":
            pass_mark = st.slider("Passing Marks", 0, 100, 40)
            passed = (df['marks'] >= pass_mark).sum()
            failed = (df['marks'] < pass_mark).sum()
            fig, ax = plt.subplots()
            ax.pie([passed, failed], labels=['Pass', 'Fail'], autopct='%1.1f%%')
            ax.set_title(f"Pass/Fail Ratio (Passing mark = {pass_mark})")
            st.pyplot(fig)