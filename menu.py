import streamlit as st
from streamlit_option_menu import option_menu
from authen_test import app


st.set_page_config(
        page_title="EQx Chatbot",
        page_icon='✔'
)


class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": function,
        })

    def run():
        # app = st.sidebar(
        with st.sidebar:        
            app = option_menu(
                menu_title='EQx ',
                options=['Home','Login','More'],
                # icons=['house-door-fill','box-arrow-in-right','wechat','person-fill','three-dots'],
                # menu_icon='app-indicator',
                default_index=1,
                styles={
                    "container": {"padding": "5!important","background-color":'white'},
        "icon": {"color": "black", "font-size": "23px"}, 
        "nav-link": {"color":"black","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "grey"},
        "nav-link-selected": {"background-color": "#02ab21"},}
                
                )

        
        if app == "Home":
            st.title("Elite Chat Bot ")
            st.write("Some introduction")
        if app == "Login":
            authen_test.app()          
    run()            
