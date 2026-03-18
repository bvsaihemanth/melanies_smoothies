import streamlit as st
import snowflake.connector
from snowflake.snowpark import Session

# Title
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# ✅ Create Snowflake session using secrets
session = Session.builder.configs({
    "account": st.secrets["account"],
    "user": st.secrets["user"],
    "password": st.secrets["password"],
    "warehouse": st.secrets["warehouse"],
    "database": st.secrets["database"],
    "schema": st.secrets["schema"],
    "role": st.secrets["role"]
}).create()

# Load fruit table
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")

# Show table
st.dataframe(data=my_dataframe, use_container_width=True)

# Convert to list
fruit_rows = my_dataframe.select("FRUIT_NAME").collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# Multiselect (limit 5)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Build string
ingredients_string = ""
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)
    st.write("Selected:", ingredients_string)

# Button
submit = st.button("Submit Order")

# Insert
if submit:
    if not name_on_order:
        st.error("Please enter a name")
    elif not ingredients_string:
        st.error("Please select ingredients")
    else:
        session.sql(
            "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
