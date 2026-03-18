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
# Load fruits
# -------------------------------
df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
fruit_rows = df.select("FRUIT_NAME").collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

st.dataframe(df, width="stretch")

# -------------------------------
# Select fruits
# -------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:
    st.write("Selected:", ", ".join(ingredients_list))

# -------------------------------
# Submit Order
# -------------------------------
if st.button("Submit Order"):
    if not name_on_order:
        st.error("Enter name")
    elif not ingredients_list:
        st.error("Select fruits")
    else:
        session.sql(
            "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
            params=[", ".join(ingredients_list), name_on_order]
        ).collect()

        st.success(f"Order placed for {name_on_order} ✅")

# -------------------------------
# API function
# -------------------------------
def get_fruit_data(fruit):
    url = f"https://my.smoothiefroot.com/api/fruit/{fruit}"
    try:
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            return res.json()
        return None
    except:
        return None

# -------------------------------
# Mapping
# -------------------------------
fruit_map = {
    "Blueberries": "blueberry",
    "Dragon Fruit": "dragonfruit",
    "Guava": "guava",
    "Apples": "apple",
    "Banana": "banana",
    "Mango": "mango",
    "Strawberries": "strawberry",
    "Pineapple": "pineapple",
    "Kiwi": "kiwi",
    "Orange": "orange",
    "Cantaloupe": "canteloupe"
}

# -------------------------------
# Nutrition Section
# -------------------------------
st.subheader("🍉 Nutrition Info")

if ingredients_list:

    combined_data = []
    missing = []

    for fruit in ingredients_list:

        df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS") \
            .select("FRUIT_NAME", "SEARCH_ON") \
            .collect()

        fruit_search_map = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in df}

        api_name = fruit_search_map.get(fruit)

        if not api_name:
            missing.append(fruit)
            continue

        # -------------------------------
        # STEP 1: CHECK DB
        # -------------------------------
        db_result = session.sql(
            "SELECT * FROM SMOOTHIES.PUBLIC.FRUIT_NUTRITION WHERE FRUIT_NAME = ?",
            params=[api_name]
        ).collect()

        if db_result:
            row = db_result[0]

            combined_data.append({
                "Fruit": fruit,
                "Carbs": row["CARBS"] or "N/A",
                "Fat": row["FAT"] or "N/A",
                "Protein": row["PROTEIN"] or "N/A",
                "Sugar": row["SUGAR"] or "N/A"
            })

            continue

        # -------------------------------
        # STEP 2: CALL API
        # -------------------------------
        data = get_fruit_data(api_name)

        if data and "nutrition" in data:

            n = data["nutrition"]

            carbs = n.get("carbs")
            fat = n.get("fat")
            protein = n.get("protein")
            sugar = n.get("sugar")

            # -------------------------------
            # STEP 3: INSERT INTO DB
            # -------------------------------
            session.sql(
                """INSERT INTO SMOOTHIES.PUBLIC.FRUIT_NUTRITION
                (FRUIT_NAME, CARBS, FAT, PROTEIN, SUGAR)
                VALUES (?, ?, ?, ?, ?)""",
                params=[api_name, carbs, fat, protein, sugar]
            ).collect()

            st.write(f"Inserted into DB: {api_name}")  # DEBUG LINE

            combined_data.append({
                "Fruit": fruit,
                "Carbs": carbs or "N/A",
                "Fat": fat or "N/A",
                "Protein": protein or "N/A",
                "Sugar": sugar or "N/A"
            })

        else:
            missing.append(fruit)

    # -------------------------------
    # SHOW TABLE
    # -------------------------------
    if combined_data:
        st.dataframe(combined_data, width="stretch")

    if missing:
        st.warning(f"❌ No data for: {', '.join(missing)}")
