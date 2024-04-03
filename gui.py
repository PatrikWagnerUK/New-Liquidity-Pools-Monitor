import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Function to load data from URLs with caching and additional error handling
@st.cache(allow_output_mutation=True)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.sort_values(by='timestamp', ascending=False, inplace=True)
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def execute_app():
    # Sidebar for database selection and refresh button
    st.set_page_config(layout="wide")
    st.sidebar.header("Database Selection and Actions")
    db_urls = {
        "Database 1": "https://pwagner.eu.pythonanywhere.com/scripts/static/token_database.csv",
        "Database 2": "https://pwagner.eu.pythonanywhere.com/scripts/static/token_database_all.csv"
    }
    db_choice = st.sidebar.selectbox("Choose the database:", options=list(db_urls.keys()))

    # Button for refreshing data
    if st.sidebar.button("Refresh Data"):
        # This will clear the cache and force all cached functions to rerun
        st.legacy_caching.clear_cache()
        st.experimental_rerun()

    # Display data from the selected database
    data = load_data(db_urls[db_choice])
    if not data.empty:
        st.dataframe(data)
    else:
        st.write("No data available or file not found.")