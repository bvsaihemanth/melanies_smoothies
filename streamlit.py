# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Title
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# 🔥 Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get Snowflake session
session = get_active_session()

# Load fruit table
my_dataframe = session.table("smoothies.public.fruit_options")

# Show table
st.dataframe(data=my_dataframe, use_container_width=True)

# Convert Snowpark → Python list
fruit_rows = my_dataframe.select("FRUIT_NAME").collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# Multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list
)

# Build ingredients string
ingredients_string = ''
if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    st.write(ingredients_string)

# 🔥 Build SQL (UPDATED with name)
my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

# Show SQL (for debugging as per lab)
st.write(my_insert_stmt)

# Button
time_to_insert = st.button('Submit Order')

# Insert ONLY on button click
if time_to_insert:
    if ingredients_string:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")