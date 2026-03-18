import streamlit as st
import requests
from snowflake.snowpark import Session

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
# Load fruit options
# -------------------------------
df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
st.dataframe(df, width="stretch")

fruit_rows = df.select("FRUIT_NAME").collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# -------------------------------
# Multiselect
# -------------------------------
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
# API Function (SAFE + CACHED)
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

# -------------------------------
# Nutrition Section (COMBINED)
# -------------------------------
st.subheader("🍉 Nutrition Info")

if ingredients_list:

    combined_data = []
    missing_fruits = []

    for fruit in ingredients_list:
        api_name = fruit_map.get(fruit)

        # ❌ Not mapped
        if not api_name:
            missing_fruits.append(fruit)
            continue

        data = get_fruit_data(api_name)

        # ✅ Valid response
        if data and "nutrition" in data:
            nutrition = data["nutrition"]

            combined_data.append({
                "Fruit": fruit,
                "Carbs": nutrition.get("carbs"),
                "Fat": nutrition.get("fat"),
                "Protein": nutrition.get("protein"),
                "Sugar": nutrition.get("sugar")
            })
        else:
            missing_fruits.append(fruit)

    # -------------------------------
    # Show combined table
    # -------------------------------
    if combined_data:
        st.dataframe(combined_data, width="stretch")

    # -------------------------------
    # Show missing fruits
    # -------------------------------
    if missing_fruits:
        st.warning(f"❌ No nutrition data for: {', '.join(missing_fruits)}")
