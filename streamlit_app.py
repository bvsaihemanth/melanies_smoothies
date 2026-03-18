import streamlit as st
import snowflake.connector
from snowflake.snowpark import Session

# Title
st.title("🥤 Customize Your Smoothie!")

# 🔥 Read secrets directly
conn = snowflake.connector.connect(
    account="svb09192.us-west-2",
    user="hemanth",
    password=st.secrets["7rg7P5e8vw3vE7B"],
    role="SYSADMIN",
    warehouse="COMPUTE_WH",
    database="SMOOTHIES",
    schema="PUBLIC",
    authenticator="snowflake",
    client_session_keep_alive=True
)

session = Session.builder.configs({
    "account": "svb09192.us-west-2",
    "user": "hemanth",
    "password": st.secrets["7rg7P5e8vw3vE7B"],
    "warehouse": "COMPUTE_WH",
    "database": "SMOOTHIES",
    "schema": "PUBLIC",
    "role": "SYSADMIN"
}).create()
