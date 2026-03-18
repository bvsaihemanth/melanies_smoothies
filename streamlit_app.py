import streamlit as st
import requests
from snowflake.snowpark import Session

# -------------------------------
# Title
# -------------------------------
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# -------------------------------
# Mode Toggle
# -------------------------------
mode = st.radio(
    "Select Mode:",
    ["Single Fruit (Badge Mode)", "Multiple Fruits (Advanced Mode)"]
)

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
# Load fruit options
# -------------------------------
df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
st.dataframe(df, width="stretch")

fruit_rows = df.select("FRUIT_NAME").collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# -------------------------------
# API Function (FIXED)
# -------------------------------
@st.cache_data
def get_fruit_data(fruit):
    url = f"https://my.smoothiefroot.com/api/fruit/{fruit}"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

# -------------------------------
# Mapping
# -------------------------------
fruit_map = {
    "Blueberries": "blueberry",
    "Elderberries": "elderberry",
    "Dragon Fruit": "dragonfruit",
    "Guava": "guava",
    "Jackfruit": "jackfruit",
    "Apples": "apple",
    "Mango": "mango",
    "Banana": "banana",
    "Strawberries": "strawberry",
    "Pineapple": "pineapple",
    "Kiwi": "kiwi",
    "Lime": "lime",
    "Orange": "orange",
    "Cantaloupe": "canteloupe"
}

# =========================================================
# 🟢 MODE 1: SINGLE FRUIT (BADGE MODE)
# =========================================================
if mode == "Single Fruit (Badge Mode)":

    fruit_choice = st.selectbox("Choose a fruit:", fruit_list)

    if fruit_choice:
        api_name = fruit_map.get(fruit_choice)

        if api_name:
            data = get_fruit_data(api_name)

            if data and "nutrition" in data:
                nutrition = data["nutrition"]

                st.dataframe([{
                    "carbs": nutrition.get("carbs"),
                    "fat": nutrition.get("fat"),
                    "protein": nutrition.get("protein"),
                    "sugar": nutrition.get("sugar")
                }], width="stretch")

            else:
                st.warning("No nutrition data available")

        else:
            st.warning("Fruit not supported by API")

# =========================================================
# 🔵 MODE 2: MULTIPLE FRUITS (ADVANCED)
# =========================================================
else:

    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_list,
        max_selections=5
    )

    ingredients_string = ", ".join(ingredients_list) if ingredients_list else ""

    if ingredients_list:
        st.write("Selected:", ingredients_string)

    # -------------------------------
    # Submit Order
    # -------------------------------
    if st.button("Submit Order"):
        if not name_on_order:
            st.error("Please enter a name")
        elif not ingredients_string:
            st.error("Please select ingredients")
        else:
            session.sql(
                "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
                params=[ingredients_string, name_on_order]
            ).collect()

            st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

    # -------------------------------
    # Nutrition Section
    # -------------------------------
    st.subheader("🍉 Nutrition Info")

    if ingredients_list:
        missing_fruits = []

        for fruit in ingredients_list:
            api_name = fruit_map.get(fruit)

            if not api_name:
                missing_fruits.append(fruit)
                continue

            data = get_fruit_data(api_name)

            if data and "nutrition" in data:
                st.markdown(f"### {fruit}")

                nutrition = data["nutrition"]

                st.dataframe({
                    "Nutrient": list(nutrition.keys()),
                    "Value": list(nutrition.values())
                })

            else:
                missing_fruits.append(fruit)

        if missing_fruits:
            st.warning(f"❌ No nutrition data for: {', '.join(missing_fruits)}")
