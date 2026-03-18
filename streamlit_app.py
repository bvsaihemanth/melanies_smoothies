import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# -------------------------------
# Title
# -------------------------------
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# -------------------------------
# Name input
# -------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# -------------------------------
# Snowflake Session
# -------------------------------
session = Session.builder.configs({
    "account": st.secrets["account"],
    "user": st.secrets["user"],
    "password": st.secrets["password"],
    "warehouse": st.secrets["warehouse"],
    "database": st.secrets["database"],
    "schema": st.secrets["schema"],
    "role": st.secrets["role"]
}).create()

# -------------------------------
# Load fruit data (with SEARCH_ON)
# -------------------------------
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Show table (optional)
st.dataframe(pd_df, width="stretch")

# -------------------------------
# Multiselect
# -------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# -------------------------------
# Build string
# -------------------------------
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write("Selected:", ingredients_string)

# -------------------------------
# Submit Order
# -------------------------------
if st.button("Submit Order"):
    if not name_on_order:
        st.error("Please enter a name")
    elif not ingredients_list:
        st.error("Please select ingredients")
    else:
        session.sql(
            "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

# -------------------------------
# Nutrition Info
# -------------------------------
st.subheader("🍉 Nutrition Information")

if ingredients_list:

    for fruit_chosen in ingredients_list:

        # 🔥 Get SEARCH_ON value from dataframe
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.write("The search value for", fruit_chosen, "is", search_on)

        st.subheader(fruit_chosen + " Nutrition Information")

        # 🔥 IMPORTANT: use search_on (NOT fruit_chosen)
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        data = response.json()

        # Handle API response
        if "nutrition" in data:
            nutrition = data["nutrition"]

            st.dataframe({
                "Nutrient": list(nutrition.keys()),
                "Value": list(nutrition.values())
            }, width="stretch")

        else:
            st.write("❌ Not found in API")
