import openai
import pandas as pd
import sqlite3
import streamlit as st
import time
from openai import OpenAI

# Show title and description.
st.title("Elite Chat Bot with Document(V1)")
st.write(
    "Hello, this is our new app you can chat with! Please upload the csv document of ranks below and ask questions about it."
    "Currently, to use this app, you need to fill in the API key I provided. Please don't use your own API key because it may bring bugs ;( "
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key, base_url="https://api.deepseek.com")
    
    uploaded_file = st.file_uploader("Upload a document (.csv)", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("File uploaded successfully!")

        # Create an in-memory SQLite database
        conn = sqlite3.connect(':memory:')

        # Write the DataFrame to the SQLite database
        try:
            df.to_sql('excel_data', conn, index=False, if_exists='replace')
            st.write("DataFrame has been successfully written to the database.")
        except Exception as e:
            st.write(f"An error occurred while writing to the database: {e}")

        # Check if the table has been successfully written to the database
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            st.write(f"Tables in the database: {tables}")
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

        sysprompt = "Your task is to study and understand the structure and specific values of a large dataset, and then answer questions based on it. The dataset records a collection of elite quality indices calculated through a hierarchical tree structure, encompassing over one hundred and fifty countries. Specifically, a PEQX index is calculated for each country. The score of PEQX is derived from the values of 'Index Areas', which represent the indices at the next lower level. In turn, the scores of these subordinate level indicators are calculated from the values of indices at an even lower level within the hierarchy.\n\n# Dataset description:\n\n## Index Levels:\n- **PEQX:** Overall index for each country.\n- **Index Area:** Specific areas contributing to the PEQX score.\n- **Pillar:** Sub-components of each Index Area.\n- **Indicator:** Detailed metrics contributing to each Pillar.\n\n## Column Names:\nThe dataset columns are structured as follows:\n- **Country Name**\n- **Country Code**\n- **Index Level**\n- **Index Element Code**\n- **Index Element Name**\n- Yearly scores from 2005 to 2024.\n\nHigher scores indicate better performance. Each row records a score for each year, allowing for year-over-year comparisons.\n\n## Example Rows:\n\n### PEQX Level:\n```\nCountry Name | Country Code | Index Level | Index Element Code | Index Element Name | 2024 | 2023 | 2022 | 2021 | 2020 | 2019 | 2018 | 2017 | 2016 | 2015 | 2014 | 2013 | 2012 | 2011 | 2010 | 2009 | 2008 | 2007 | 2006 | 2005\nAustralia    | AUS          | PEQX        | PEQX               | PEQX               | 52.906 | 52.906 | 52.893 | 51.923 | 50.719 | 51.41  | 52.793 | 53.638 | 57.133 | 53.876 | 53.66  | 55.322 | 56.886 | 55.08  | 55.924 | 57.318 | 54.402 | 54.219 | 52.602 | 53.982\nFinland      | FIN          | PEQX        | PEQX               | PEQX               | 58.781 | 58.781 | 59.432 | 58.529 | 58.909 | 56.828 | 56.391 | 57.998 | 60.242 | 58.772 | 61.626 | 62.88  | 61.055 | 62.554 | 62.959 | 60.34  | 61.454 | 62.713 | 61.67  | 62.46\n```\n\n### Index Area Level:\n```\nCountry Name | Country Code | Index Level | Index Element Code | Index Element Name | 2024 | 2023 | 2022 | 2021 | 2020 | 2019 | 2018 | 2017 | 2016 | 2015 | 2014 | 2013 | 2012 | 2011 | 2010 | 2009 | 2008 | 2007 | 2006 | 2005\nAustralia    | AUS          | Index Area  | i                  | Political Power    | 64.438 | 64.438 | 64.536 | 62.929 | 63.495 | 62.078 | 62.319 | 63.425 | 65.557 | 65.049 | 64.444 | 64.37  | 64.411 | 65.081 | 64.786 | 63.978 | 63.98  | 63.275 | 62.706 | 63.609\nBelgium      | BEL          | Index Area  | iii                | Political Value    | 49.175 | 49.175 | 49.306 | 48.765 | 47.145 | 46.678 | 47.038 | 46.19  | 44.031 | 46.12  | 45.76  | 46.161 | 44.679 | 45.217 | 45.986 | 43.958 | 45.352 | 46.477 | 45.564 | 46.772\n```\n\n### Pillar Level:\n```\nCountry Name | Country Code | Index Level | Index Element Code | Index Element Name | 2024 | 2023 | 2022 | 2021 | 2020 | 2019 | 2018 | 2017 | 2016 | 2015 | 2014 | 2013 | 2012 | 2011 | 2010 | 2009 | 2008 | 2007 | 2006 | 2005\nAustralia    | AUS          | Pillar      | iii.7              | Giving Income      | 64.854 | 64.854 | 64.854 | 63.603 | 63.755 | 63.822 | 64.143 | 64.058 | 64.329 | 64.157 | 63.542 | 64.076 | 63.039 | 63.928 | 65.246 | 63.015 | 62.222 | 63.851 | 63.047 | 63.535\nBelgium      | BEL          | Pillar      | iv.12              | Labor Value        | 36.212 | 36.212 | 41.374 | 47.572 | 62.302 | 53.273 | 50.11  | 39.689 | 54.804 | 50.355 | 54.924 | 51.411 | 50.547 | 47.617 | 49.953 | 52.029 | 44.481 | 44.299 | 38.984 | 46.656\n```\n\n### Indicator Level:\n```\nCountry Name | Country Code | Index Level | Index Element Code | Index Element Name | 2024 | 2023 | 2022 | 2021 | 2020 | 2019 | 2018 | 2017 | 2016 | 2015 | 2014 | 2013 | 2012 | 2011 | 2010 | 2009 | 2008 | 2007 | 2006 | 2005\nAustralia    | AUS          | Indicator   | i.1_INE            | Top 10% share of pre-tax national income | 63.778 | 63.778 | 63.778 | 63.899 | 64.225 | 63.891 | 60.614 | 59.04  | 60.721 | 59.698 | 57.66  | 58.307 | 56.748 | 56.812 | 57.838 | 55.533 | 59.739 | 62.761 | 63.648 | 64.362\nBelgium      | BEL          | Indicator   | iii.9_CDD          | CO2 emissions embodied in domestic final demand per capita | 31.635 | 31.635 | 31.635 | 31.635 | 31.635 | 31.635 | 31.635 | 32.106 | 31.992 | 30.87  | 32.523 | 32.655 | 31.696 | 31.844 | 31.676 | 33.784 | 31.917 | 36.33  | 35.712 | 33.263\n```\n\n# User Queries:\n- Users may ask to compare the latest scores between countries for a specific index.\n  - Example: \"Compare how South Korea and China are doing in Political Power.\"\n- Users may request to compare the development of scores over time.\n  - Example: \"Describe the development of Political Power in South Korea from 2010 to 2024.\"\n\nWhen answering, focus on the latest year for direct comparisons and on year-over-year trends for developmental queries."

        question = st.text_area(
            "Now ask a question about the document!",
            placeholder="For example: According to the excel of Country ranks, which 10 countries were the worst in 2020?",
        )


        # Function to handle API calls with retry mechanism
        def call_openai_with_retry(call_function, max_retries=30, delay=50):
            """
            General API call function with retry mechanism
            """
            retries = 0
            while retries < max_retries:
                try:
                    return call_function()
                except openai.error.RateLimitError as e:
                    print(f"RateLimitError: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    retries += 1
            raise Exception("Max retries exceeded")
        
        # Function to classify the question using OpenAI API
        def classify_question_with_openai(question):
            """
            Classify the question using OpenAI API to determine if it requires using Excel data
            """
            def api_call():
                response = client.chat.completions.create(
                    #model="gpt-3.5-turbo",
                    model="deepseek-chat",
                    messages=[
                        {
                            "role": "system",
                            "content": f"remember,{sysprompt}.Here you have a question from user: {question}.now determine:Do you think SQL can help answer this question? Please only respond with 'yes' or 'no':"
                        },
                        {"role": "user", "content": question},
                    ],
                    stream=False,
                )
                print(response.choices[0].message.content)
                return response.choices[0].message.content

            answer = call_openai_with_retry(api_call)
            return "use_excel" if answer == "yes" else "no_excel"
        
        # Function to generate SQL query using OpenAI API based on the question and table structure
        def generate_sql_query_with_openai(question, table_structure):
            """
            Generate SQL query using OpenAI API based on the question and table structure
            """
            def api_call():
                structure_str = ', '.join([f"{col} ({dtype})" for col, dtype in table_structure.items()])
                prompt = (f"Based on the following question and table structure, generate a pure SQL query. Note that column names such as '2005' should be enclosed in quotes."
                        f"This Table is regarding ranks. So, larger number means worse performance. Table name: excel_data. Table structure: {structure_str}. Question: {question}"
                        f"Do not include any extra characters or markdown, only return the SQL code. ")
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
                return response.choices[0].message.content

            sql_query = call_openai_with_retry(api_call)
            print(sql_query)
            cleaned_sql_query = clean_sql_query(sql_query)
            print(cleaned_sql_query)
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
            return result

        # Function to generate an answer using OpenAI API based on the query results
        def generate_answer_with_openai(question, result=None):
            """
            Generate an answer using OpenAI API based on the query results
            """
            def api_call():
                if result is not None:
                    result_str = str(result)
                    prompt = f"{sysprompt}Now, according to the SQL result data: {result_str}, produce an answer to this question: {question}."
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

            answer = call_openai_with_retry(api_call)
            return answer
        
        # Main function to generate the answer
        def answer_question(question):
            """
            Main function to generate the answer
            """
            question_type = classify_question_with_openai(question)
            if question_type == "use_excel":
                sql_query = generate_sql_query_with_openai(question, table_structure)
                result = execute_sql_query(sql_query)
                answer = generate_answer_with_openai(question, result)
            else:
                answer = generate_answer_with_openai(question)
            
            return answer

        if question:
            answer1 = answer_question(question)

            st.write(answer1)
