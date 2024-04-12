# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session  ## commented out as this is not used if we do SniS, instead,add cnx=st.connection("snowflake") line
from snowflake.snowpark.functions import col
# streamlit documentation: https://docs.streamlit.io/library/api-reference/widgets/st.text_input

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """choose the fruits you want in your custom smoothies!
    """)

name_on_order= st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be', name_on_order)

# add below line when using as SniS
cnx=st.connection("snowflake")
session=cnx.session()
# session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
# st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list=st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5,
)

if ingredients_list:
    # st.write(ingredients_list)
    # st.text(ingredients_list)
    ingredients_string = ''
    for x in ingredients_list:
        ingredients_string += x + ' '
    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    # the above is the sql will be executed to insert values into table
    
    st.write(my_insert_stmt) # print out for debug
    # st.stop() # Stop command is for troubleshooting. Check before app write to database
    
    time_to_insert = st.button('Submit order') # create a button to trigger sql
    
    if time_to_insert:
        session.sql(my_insert_stmt,params=(ingredients_string, name_on_order)).collect() # send to sql
        st.success(f'Your Smoothie is ordered, {name_on_order}!',icon="✅")
    
## Let's Call the Fruityvice API from Our SniS App!
import requests
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
# st.text(fruityvice_response.json())
fv_df=st.dataframe(data=fruityvice_response.json(),use_container_width=True)
