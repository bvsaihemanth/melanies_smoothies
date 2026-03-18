# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Title
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# 🔥 Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# ✅ Snowflake connection (SniS)
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit table
my_dataframe = session.table("smoothies.public.fruit_options")

# Show table
st.dataframe(data=my_dataframe, use_container_width=True)

# Convert Snowpark → Python list
fruit_rows = my_dataframe.select("FRUIT_NAME").collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# ✅ Multiselect with limit
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Build ingredients string
ingredients_string = ''
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    st.write("Selected Ingredients:", ingredients_string)

# Button
time_to_insert = st.button('Submit Order')

# ✅ Safe Insert with validation
if time_to_insert:

    if not name_on_order:
        st.error("Please enter a name")
    
    elif not ingredients_string:
        st.error("Please select at least one ingredient")

    else:
        try:
            session.sql(
                "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
                params=[ingredients_string, name_on_order]
            ).collect()

            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

        except Exception as e:
            st.error(f"Error placing order: {e}")
