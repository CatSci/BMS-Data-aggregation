import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
import streamlit as st

def read_file(uploaded_files):
    """_summary_

    Args:
        uploaded_files (_type_): _description_

    Returns:
        _type_: _description_
    """
    for uploaded_file in uploaded_files:
        if "Order" in uploaded_file.name and "xlsx" in uploaded_file.name:
            order_df = pd.read_excel(uploaded_file)
            # st.write(uploaded_file.name)
            # st.write(order_df.shape)
        
        else:
            bms_df = pd.read_excel(uploaded_file)
            # st.write(uploaded_file.name)
            # st.write(bms_df.shape)

    return order_df, bms_df


def fill_data(bms_dataframe, order_dataframe):
    """_summary_

    Args:
        bms_dataframe (_type_): _description_
        order_dataframe (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Create a set to store duplicate 'Order No.' values
    duplicate_order_numbers = set()
    encountered_order_numbers = set()
    c = 0
    # Iterate through rows in bms_report_df
    for idx, row in bms_dataframe.iterrows():
        order_no = row['Order No.']
        order_desc = row["Material Description"]
        # Check if 'Order No.' is not NaN
        if not pd.isna(order_no) and not pd.isna(order_desc):
            # Check if the order_no has been encountered before
            if order_no in encountered_order_numbers:
                # Add it to the duplicate_order_numbers set
                duplicate_order_numbers.add(order_no)
            else:
                # Otherwise, add it to the encountered_order_numbers set
                encountered_order_numbers.add(order_no)
            # Search for the corresponding row in order_df where 'PO No.' matches 'Order No.'
            matching_rows = order_dataframe[order_dataframe['PO No.'] == order_no]
            
            if not matching_rows.empty:
                # Extract data from the first matching row in order_df
                for index, matching_row in matching_rows.iterrows():
                    matching_desc = matching_row['Product Description']
                    similarity = 1 - Levenshtein.distance(order_desc, matching_desc) / max(len(order_desc), len(matching_desc))
                    if similarity > 0.60:
                        size = matching_row['Size']
                        unit_of_measure = matching_row['Unit of Measure']
                        quantity = matching_row['Quantity']
                        cas = matching_row['CAS #']
                        

                        bms_dataframe.at[idx, 'Size'] = size
                        bms_dataframe.at[idx, 'Unit of Measure'] = unit_of_measure
                        bms_dataframe.at[idx, 'Quantity'] = quantity
                        bms_dataframe.at[idx, 'CAS #'] = cas
    
    return bms_dataframe, duplicate_order_numbers


def convert_duplicate_order_to_dataframe(duplicate_order_numbers):
    """_summary_

    Args:
        duplicate_order_numbers (_type_): _description_

    Returns:
        _type_: _description_
    """
    duplicate_order_numbers_list = list(duplicate_order_numbers)
    # Create a dataframe with the list of duplicate 'Order No.' values
    duplicate_order_df = pd.DataFrame({'Duplicate Order No.': list(duplicate_order_numbers)})

    return duplicate_order_df


def remove_shipping(bms_dataframe):
    """_summary_

    Args:
        bms_dataframe (_type_): _description_

    Returns:
        _type_: _description_
    """
    processed_rows = set()
    rows_to_remove = []
    extra_charges = ["Shipping", "shipping", "Shipping/Handling Charges", "Carriage", "Freight"]
    
    for index, row in bms_dataframe.iterrows():
        for charge in extra_charges:
            if pd.notna(row["Material Description"]) and charge in row["Material Description"]:
                if index not in processed_rows:
                    price = row["Inv Value  Currency-Original"]
                    description = row["Material Description"]
                    st.write(f" Index {index} Description {description} and Price {price}")
                    value = bms_dataframe.at[index - 1, "Inv Value  Currency-Original"]
                    st.write(value)
                    if value < 0:
                        st.write("at -2 index")
                        bms_dataframe.at[index - 2, 'Other Costs'] = float(price)
                        bms_dataframe.at[index - 2, 'Specify Other Cost'] = description
                    else:
                        st.write("at -1 index")
                        bms_dataframe.at[index - 1, 'Other Costs'] = float(price)
                        bms_dataframe.at[index - 1, 'Specify Other Cost'] = description
                    rows_to_remove.append(index)
                    processed_rows.add(index)  # Mark the row as processed

    
    return bms_dataframe, rows_to_remove

# Function to calculate 'Cost in USD' based on the specified conditions
def calculate_cost(row):
    inv_value = row['Inv Value  Currency-Original']
    other_costs = row['Other Costs']

    # Check for NaN or missing values and handle them
    if pd.isna(inv_value):
        inv_value = 0
    if pd.isna(other_costs):
        other_costs = 0

    # Calculate 'Cost in USD'
    cost_in_usd = inv_value + other_costs
    return cost_in_usd