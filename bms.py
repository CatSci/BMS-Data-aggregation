import streamlit as st
import pandas as pd

from utils import read_file, fill_data, remove_shipping, convert_duplicate_order_to_dataframe, calculate_cost, change_date_format

# hide streamlit style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)
# background-color: #ed9439;
st.markdown("""
<style>
.navbar {
  height: 80px;
  background-color: #ed9439;
  color: #ed9439;
}
.navbar-brand{
    font-size: 40px;
    margin-left:40px;
}
</style>""", unsafe_allow_html= True)


st.markdown("""
<nav class="navbar fixed-top navbar-expand-lg navbar-dark">
  <a class="navbar-brand" href="#" target="_blank">CatSci</a>
  

</nav>
""", unsafe_allow_html=True)

st.title('BMS Order Data Aggregation')

uploaded_files = st.file_uploader("Choose a file", accept_multiple_files= True)


if st.button("Done") and uploaded_files is not None:
    with st.spinner('Please wait...'):
        order_df, bms_df = read_file(uploaded_files)
        # st.data_editor(bms_df)

        bms_dataframe, duplicate_po_number = fill_data(bms_dataframe= bms_df, order_dataframe= order_df)
        bms_dataframe, rows_to_remove = remove_shipping(bms_dataframe = bms_dataframe)
        
        duplicate_order_number = convert_duplicate_order_to_dataframe(duplicate_order_numbers= duplicate_po_number)
        final_df = bms_dataframe.drop(rows_to_remove)
        final_df['Cost in USD'] = final_df.apply(calculate_cost, axis=1)
        final_df = change_date_format(final_df)
        st.dataframe(final_df)
        st.dataframe(duplicate_order_number)
    


