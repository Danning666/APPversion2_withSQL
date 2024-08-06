import openai
import pandas as pd
import sqlite3
import streamlit as st
import time
from openai import OpenAI
from st_files_connection import FilesConnection

# Show title and description.
st.title("Elite Chat Bot (V2)")
st.write(
    "Hello, welcome to our chatAPP v2! "
    "Please use the check box to change the mode"
)

if 'question_type' not in st.session_state:
    st.session_state.question_type = None

# Ask user for their OpenAI API key via `st.text_input`.
#openai_api_key = st.text_input("OpenAI API Key", type="password")
openai_api_key =  st.secrets["current_key"]
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key, base_url="https://api.deepseek.com")
    
    #uploaded_file = st.file_uploader("Upload a document (.csv)", type="csv")
    conn = st.connection('s3', type=FilesConnection)
    #df = conn.read("testbucket-jrieke/myfile.csv", input_format="csv", ttl=600)
    df = conn.read("elitestreamlitdanning/wb_PEQx2024_ranks_all.csv", input_format="csv", ttl=600)
  
    #if uploaded_file:
        #df = pd.read_csv(uploaded_file)

    st.write("File fetched successfully!")

    # Create an in-memory SQLite database
    conn = sqlite3.connect(':memory:')

    # Write the DataFrame to the SQLite database
    try:
        df.to_sql('excel_data', conn, index=False, if_exists='replace')
        #st.write("DataFrame has been successfully written to the database.")
    except Exception as e:
        st.write(f"An error occurred while writing to the database: {e}")

    # Check if the table has been successfully written to the database
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        #st.write(f"Tables in the database: {tables}")
    except Exception as e:
        st.write(f"An error occurred while checking the table: {e}")
    def get_table_structure():
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(excel_data)")
        columns = cursor.fetchall()
        table_structure = {column[1]: column[2] for column in columns}  # Dictionary format: {column_name: data_type}
        return table_structure

    # Get the table structure
    table_structure = get_table_structure()
    print(table_structure)

    sysprompt = pd.read_csv("pbaliu.txt")
    question = st.text_area(
        "Now ask a question please",
        placeholder="For example: According to the excel of Country ranks, which 10 countries were the worst in 2020?",
    )


    genre = st.radio(
        "Which mode would you like to use?",
        [":rainbow[withSQL]", "***Pure API***"],
        captions=[
            "Will generate SQL Code first and analyze based on it",
            "Will analyze immediately"
        ],
        help="Choose a mode to proceed",
        index=None,
        key="mode_selector"
    )

    
    
    # Function to generate SQL query using OpenAI API based on the question and table structure
    def generate_sql_query_with_openai(question, table_structure):
        """
        Generate SQL query using OpenAI API based on the question and table structure
        """
        structure_str = ', '.join([f"{col} ({dtype})" for col, dtype in table_structure.items()])
        prompt = (f"{sysprompt}Based on the following question and table structure, generate a pure SQL query. Make sure to extract as much as possible information in the query For example, when asked about certain countries performance, please take the countries ranks data of all index levels. Note that column names such as '2005' should be enclosed in quotes."
                f"This Table is regarding ranks. So, larger number means worse performance. Table name: excel_data. Table structure: {structure_str}. Question: {question}"
                f"Please use the right columns name and only produce one SQL query.Do not include any extra characters or markdown, only return one clean SQL code. Please note that columns names are like 'Country Name', not 'Country_Name'. ")
        response = client.chat.completions.create(
            model="deepseek-chat",
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
    def execute_sql_query(sql_query):
        """
        Execute the SQL query and return the results
        """
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        st.sidebar.subheader("SQL Result")
        st.sidebar.write(result)
        return result

    # Function to generate an answer using OpenAI API based on the query results
    def generate_answer_with_openai(question, result=None):
        """
        Generate an answer using OpenAI API based on the query results
        """
        if result is not None:
            result_str = str(result)
            prompt = f"{sysprompt}Now, according to the SQL result data: {result_str}, analyze it and produce an insightful answer to this question: {question}."
        else:
            document = df.to_string(index=False)
            prompt = f"{question}. You have data as followed: {document}"

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {"role": "user", "content": "."},
            ],
            stream=False,
        )
        return response.choices[0].message.content

    
    # Main function to generate the answer
    def answer_question(question,genre):
        """
        Main function to generate the answer
        """
        # question_type = classify_question_with_openai(question)
        # if st.session_state.question_type == "yes":
        if genre == ":rainbow[withSQL]":
            sql_query = generate_sql_query_with_openai(question, table_structure)
            result = execute_sql_query(sql_query)
            answer = generate_answer_with_openai(question, result)
        else:
            answer = generate_answer_with_openai(question)
        
        return answer


    if st.button("Confirm"):
        if question:
            st.write("You selected:", genre)
            if genre == ":rainbow[withSQL]":
                st.session_state.question_type = "yes"
            else:
                st.session_state.question_type = "no"
            answer1 = answer_question(question,genre)
            st.write(answer1)
