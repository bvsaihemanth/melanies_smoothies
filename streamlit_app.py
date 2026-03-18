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
# API Function
# -------------------------------
def get_fruit_data(fruit):
    url = f"https://my.smoothiefroot.com/api/fruit/{fruit}"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.json()
        return None
    except:
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
# Nutrition Section
# -------------------------------
st.subheader("🍉 Nutrition Info")

if ingredients_list:

    combined_data = []
    missing_fruits = []

    for fruit in ingredients_list:

        # -------------------------------
        # STEP 1: CHECK DB FIRST
        # -------------------------------
        result = session.sql(
            "SELECT * FROM SMOOTHIES.PUBLIC.FRUIT_NUTRITION WHERE FRUIT_NAME = ?",
            params=[fruit]
        ).collect()

        if result:
            row = result[0]

            combined_data.append({
                "Fruit": fruit,
                "Carbs": row["CARBS"] or "N/A",
                "Fat": row["FAT"] or "N/A",
                "Protein": row["PROTEIN"] or "N/A",
                "Sugar": row["SUGAR"] or "N/A"
            })

            continue

        # -------------------------------
        # STEP 2: CALL API (ONLY IF NEEDED)
        # -------------------------------
        api_name = fruit_map.get(fruit)

        if not api_name:
            missing_fruits.append(fruit)
            continue

        data = get_fruit_data(api_name)

        if data and "nutrition" in data:
            nutrition = data["nutrition"]

            carbs = nutrition.get("carbs")
            fat = nutrition.get("fat")
            protein = nutrition.get("protein")
            sugar = nutrition.get("sugar")

            # -------------------------------
            # STEP 3: STORE IN DB
            # -------------------------------
            session.sql(
                """INSERT INTO SMOOTHIES.PUBLIC.FRUIT_NUTRITION 
                (FRUIT_NAME, CARBS, FAT, PROTEIN, SUGAR)
                VALUES (?, ?, ?, ?, ?)""",
                params=[fruit, carbs, fat, protein, sugar]
            ).collect()

            combined_data.append({
                "Fruit": fruit,
                "Carbs": carbs or "N/A",
                "Fat": fat or "N/A",
                "Protein": protein or "N/A",
                "Sugar": sugar or "N/A"
            })

        else:
            missing_fruits.append(fruit)

    # -------------------------------
    # Show Table
    # -------------------------------
    if combined_data:
        st.dataframe(combined_data, width="stretch")

    # -------------------------------
    # Missing Data
    # -------------------------------
    if missing_fruits:
        st.warning(f"❌ No nutrition data for: {', '.join(missing_fruits)}")
