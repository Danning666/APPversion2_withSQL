import pandas as pd
import streamlit as st
from openai import OpenAI
from st_files_connection import FilesConnection
import json
import os
from SQL_approach import sql_function as qf


def app():


    main_dir = os.path.dirname(__file__)
    p_def_path = os.path.join(main_dir, 'build_prompts', 'prompts', 'data_def.json')
    p_sys_path = os.path.join(main_dir, 'build_prompts', 'prompts', 'data_structure.txt')

        
    # Get sys-prompt
    sysprompt = pd.read_csv(p_sys_path)


    # Show title and description.
    st.title("Elite Chat Bot (V3)")
    # st.write("Hello, welcome to our chatAPP v3! " "Please use the check box to change the mode")
    st.write(f'Welcome *{st.session_state["name"]}*')

    if "question_type" not in st.session_state:
        st.session_state.question_type = None

    # prepare the API

    client = OpenAI(api_key= st.secrets["current_key"], base_url="https://api.deepseek.com")
    OA_client = OpenAI(api_key=st.secrets["openai_api_key"])

    # Prepare the data
    conn0 = st.connection('s3', type=FilesConnection)
    df = conn0.read("elitestreamlitdanning/ranks_cut1.csv", input_format="csv", ttl=600)
    # st.write("Data fetched successfully!")



    # Get user question
    question = st.text_area(
        "Now ask a question please",
        placeholder="For example: According to the excel of Country ranks, which 10 countries were the worst in 2020?",
    )

    # Get the mode user want to use
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


    # Function to generate an answer using OpenAI API based on the query results
    def generate_answer_with_openai(client,OA_client, question, result=None):
        """
        Generate an answer using OpenAI API based on the query results
        """
        with open(p_def_path, 'r', encoding='utf-8') as file:
            try:
                document = json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error reading: {e}")
            except FileNotFoundError as e:
                print(f"File not found: {e}")
        if result is not None:
            result_str = str(result[0])
            sql_query = str(result[1])
            prompt = f"with knowdelge base: {document}. Now, for SQL query {sql_query}, we have result data: {result_str}. Please describe only integers, without any decimals, because this is a ranking dataset. Remember, smaller number of rank means better performance. Please make deep analysis of the result , instead of simply representing it, and produce an insightful answer to this question: {question}. "
        else:
            prompt = f"{document}. Now,  {question} Please always provide answer using PEQx's level structure."

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

        response2 = OA_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {"role": "user", "content": "."},
            ],
            stream=False,
        )
        return response.choices[0].message.content, response2.choices[0].message.content, 



    # Main function to generate the answer
    def answer_question(question,genre):
        """
        Main function to generate the answer
        """
        # question_type = classify_question_with_openai(question)
        # if st.session_state.question_type == "yes":
        if genre == ":rainbow[withSQL]":
            conn=qf.Data_Base_Establish(df)
            sql_query = qf.generate_sql_query_with_openai(question, client,conn,sysprompt)
            result = qf.execute_sql_query(sql_query,conn)
            answer11, answer22 = generate_answer_with_openai(client,OA_client, question, result)
        else:
            answer11, answer22 = generate_answer_with_openai(client, OA_client, question)
        
        return answer11, answer22


    if st.button("Confirm"):
        if question:
            st.write("You selected:", genre)
            if genre == ":rainbow[withSQL]":
                st.session_state.question_type = "yes"
            else:
                st.session_state.question_type = "no"
            answer1, answer2= answer_question(question,genre)

            #print
            col1, col2 = st.columns(2)


            with col1:
                st.title('Claude')
                st.write(answer1)


            with col2:
                st.title('OpenAI')
                st.write(answer2)
            






