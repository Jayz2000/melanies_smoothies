import streamlit as st
#from snowflake.snowpark.context import get_active_session  ## commented out as this is not used if we do SniS, instead,add cnx=st.connection("snowflake") line
from snowflake.snowpark.functions import col
import requests
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
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the SnowPark DataFrame to a Pandas DataFrame so we can use the LOC Function
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list=st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5,
)

if ingredients_list:
    # st.write(ingredients_list)
    # st.text(ingredients_list)
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.') # this print out the fruit_name and fruit_search_on

        st.subheader(fruit_chosen + 'Nutrition information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + str(search_on))
        fv_df=st.dataframe(data=fruityvice_response.json(),use_container_width=True)
    
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
    



