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
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
st.dataframe(my_dataframe, use_container_width=True)

# Convert to list
fruit_rows = my_dataframe.select("FRUIT_NAME").collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# -------------------------------
# Multiselect
# -------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Build ingredients string
ingredients_string = ""
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write("Selected:", ingredients_string)

# -------------------------------
# Submit Order
# -------------------------------
submit = st.button("Submit Order")

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

# -------------------------------
# API Section
# -------------------------------
st.subheader("🍉 Nutrition Info")

@st.cache_data
def get_fruit_data(fruit):
    url = f"https://my.smoothiefroot.com/api/fruit/{fruit}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    return None

# 🔥 Proper mapping (NO GUESSWORK)
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
    "Lime": "lime"
}

# Show nutrition dynamically
if ingredients_list:
    for fruit in ingredients_list:

        st.markdown(f"### {fruit}")

        # ✅ Use mapping
        fruit_api_name = fruit_map.get(fruit, fruit.lower())

        data = get_fruit_data(fruit_api_name)

        if data and "nutritions" in data:

            nutrition = data["nutritions"]

            nutrition_df = {
                "Nutrient": list(nutrition.keys()),
                "Value": list(nutrition.values())
            }

            st.dataframe(nutrition_df, use_container_width=True)

        else:
            st.warning(f"No data available for {fruit}")
