import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import schedule

from data_collector import collect_and_filter_data

def execute_app():
    # Function to load data from the selected CSV
    def load_data(file_path):
        try:
            df = pd.read_csv(file_path)
            df.sort_values(by='timestamp', ascending=False, inplace=True)
            return df
        except FileNotFoundError:
            st.error("File not found. Please check if the data collector is running.")
            return pd.DataFrame()

    # Sidebar for database selection
    st.set_page_config(layout="wide")
    st.sidebar.header("Database Selection")
    db_choice = st.sidebar.selectbox("Choose the database:", ["token_database.csv", "token_database_all.csv"])

    # Display data from the selected database
    data = load_data(db_choice)
    if not data.empty:
        st.dataframe(data)
    else:
        st.write("No data available or file not found.")

    # Initialize or update the last refresh timestamp
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()

    # Check if it's time to refresh (every 30 seconds)
    if datetime.now() - st.session_state.last_refresh > timedelta(seconds=30):
        st.session_state.last_refresh = datetime.now()
        st.rerun()

if __name__ == "__main__":

    execute_app()
    # Scheduling the data collection to run 20 times per minute
    schedule.every(3).seconds.do(collect_and_filter_data)
