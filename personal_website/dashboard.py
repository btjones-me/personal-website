"""personal-website Streamlit Dashboard."""

import pandas as pd
import streamlit as st

from personal_website.config import config
from personal_website.logger import logger

logger.info("Starting personal-website dashboard")

st.set_page_config(
    page_title="personal-website",
    page_icon="📊",
    layout="wide"
)

st.title("personal-website")
st.write("Using Codex & Claude Code to create a personal website")

# Sample data
data = {
    "Category": ["A", "B", "C", "D"],
    "Values": [23, 45, 56, 78],
    "Status": ["Active", "Inactive", "Active", "Active"]
}

df = pd.DataFrame(data)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sample Data")
    st.dataframe(df)

with col2:
    st.subheader("Chart")
    st.bar_chart(df.set_index("Category")["Values"])

if config.DEBUG:
    st.sidebar.write("Debug mode enabled")
    st.sidebar.json({"config": {"DEBUG": config.DEBUG, "LOG_LEVEL": config.LOG_LEVEL}})

logger.info("Dashboard rendered successfully")
