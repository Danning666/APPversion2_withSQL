from openai import OpenAI
import pandas as pd
import sqlite3
import streamlit as st
from st_files_connection import FilesConnection

def Data_Base_Establish(df):
    """
    Establishes an in-memory SQLite database and writes a DataFrame to it.
    Then checks if the table has been successfully written to the database.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be written to the database.
    """
    # Connect to an in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    
    try:
        # Write the DataFrame to the SQLite database
        df.to_sql('excel_data', conn, index=False, if_exists='replace')
        print("DataFrame has been written to the database successfully.")
    except Exception as e:
        print(f"An error occurred while writing to the database: {e}")
        return  # Exit the function if an error occurs
    
    try:
        # Check if the table has been successfully written to the database
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in the database: {tables}")
    except Exception as e:
        print(f"An error occurred while checking the table: {e}")
    return conn

# Prepare the data
@st.cache_data
def load_data_from_s3():
    conn0 = st.connection('s3', type=FilesConnection)
    df = conn0.read("elitestreamlitdanning/ranks_cut1.csv", input_format="csv", ttl=600)
    return df


def get_table_structure(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(excel_data)")
    columns = cursor.fetchall()
    table_structure = {column[1]: column[2] for column in columns}  # Dictionary format: {column_name: data_type}
    return table_structure






# Function to generate SQL query using OpenAI API based on the question and table structure
def generate_sql_query_with_openai(question,OA_client,conn,sysprompt):
    """
    Generate SQL query using OpenAI API based on the question and table structure
    """
    table_structure = get_table_structure(conn)
    structure_str = ', '.join([f"{col} ({dtype})" for col, dtype in table_structure.items()])
    prompt = (f"{sysprompt}Based on the following question and table structure, generate a pure SQL query. Make sure to extract as much as possible information in the query. For example, when asked about certain countries performance or difference, please take the countries ranks data of all index levels. Note that column names such as '2005' should be enclosed in quotes."
            f"This Table is regarding ranks. So, larger number means worse performance. Table name: excel_data. Table structure: {structure_str}. Question: {question}"
            f"# Please be careful about columns names. Please only produce one SQL query.Do not include any extra characters or markdown, only return one clean SQL code.  ")
    
    response = OA_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {"role": "user", "content": question},
            ],
            stream=False,
        )
        

    sql_query = response.choices[0].message.content
    print(sql_query)
    cleaned_sql_query = clean_sql_query(sql_query)
    st.sidebar.subheader("Clean SQL Code")
    st.sidebar.code(cleaned_sql_query, language="sql")
    return cleaned_sql_query 

# Function to clean SQL query from unwanted characters
def clean_sql_query(sql_query):
    """
    Clean the SQL query from unwanted characters like markdown or extra symbols
    """
    return sql_query.strip().replace('```sql', '').replace('```', '').strip()

# Function to execute the SQL query and return the results
def execute_sql_query(sql_query,conn):
    """
    Execute the SQL query and return the results
    """
    cursor = conn.cursor()
    cursor.execute(sql_query)
    result = cursor.fetchall()
    st.sidebar.subheader("SQL Result")
    st.sidebar.write(result)
    results = []
    results.append(result)
    results.append(sql_query)
    return results
