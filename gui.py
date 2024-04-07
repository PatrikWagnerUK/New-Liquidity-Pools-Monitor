import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Function to load data from URLs with caching and additional error handling
# @st.cache_data()
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
        "Premium Listings": "https://pwagner.eu.pythonanywhere.com/scripts/static/token_database.csv",
        "All Launched Coins": "https://pwagner.eu.pythonanywhere.com/scripts/static/token_database_all.csv"
    }
    db_choice = st.sidebar.selectbox("Choose the database:", options=list(db_urls.keys()))

    col1, col2, col3 = st.columns(3)

    with col2:
        st.title("New Liquidity Pools")
    # Display data from the selected database
    data = load_data(db_urls[db_choice])
    if not data.empty:
        st.dataframe(data)
        st.write("")
        st.header("1. Volume Momentum Indicator (VMI)")
        st.markdown(
                    """
                    - Description: This metric measures the rate of volume change over a specific period, highlighting tokens with rapidly increasing trading activity.
                    - Calculation: Compare the volume in the last hour (h1) to the average volume over the last 24 hours (h24). A significant increase could signal a breakout. Formula: VMI = (Volume_h1 / (Volume_h24 / 24)) * 100.
                    - Interpretation: A VMI greater than 100 indicates above-average trading activity in the last hour, suggesting growing interest.
                    """
                    )
        st.header("2. Volume-Price Trend (VPT)")
        st.markdown(
                    """
                    - Description: This metric combines price changes with volume to detect significant moves that could precede a breakout.
                    - Calculation: Calculate the product of the percentage price change over the last hour (using priceChange_h1) and the volume for the same period (volume_h1). Formula: VPT = PriceChange_h1 * Volume_h1.
                    - Interpretation: Higher VPT values indicate stronger, volume-backed price movements, potentially signaling a breakout.
                    """
                    )
        st.header("3. Relative Volume Index (RVI)")
        st.markdown(
                    """
                    - Description: Identifies when current trading volume significantly exceeds the typical trading volume, indicating increased interest.
                    - Calculation: Calculate the ratio of current hour volume to the average volume over a longer period (e.g., 6 hours). Formula: RVI = Volume_h1 / (Volume_h6 / 6).
                    - Interpretation: An RVI significantly greater than 1 suggests a sharp increase in trading activity.
                    """
                    )
        st.header("4. Volume Acceleration Index (VAI)")
        st.markdown(
                    """
                    - Description: Measures the acceleration of volume growth, identifying tokens where trading activity is not just rising, but the pace of increase is accelerating.
                    - Calculation: Compare volume growth over two successive periods (e.g., last 5 minutes vs. last hour). Formula: VAI = (Volume_m5 / Volume_h1) - (Volume_h1 / Volume_h6).
                    - Interpretation: Positive VAI values indicate accelerating volume, which could precede a breakout.
                    """
                    )
    else:
        st.write("No data available or file not found.")
    
    # Button for refreshing data
    if st.sidebar.button("Refresh Data"):
        # This will clear the cache and force all cached functions to rerun
        # st.legacy_caching.clear_cache()
        # st.experimental_rerun()
        data = load_data(db_urls[db_choice])

if __name__ == "__main__":
    execute_app()