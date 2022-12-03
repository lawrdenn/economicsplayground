import streamlit as st

class run_global_styling:
    def __init__(self):
        self.hide_menu()

    @st.cache
    def hide_menu(self):
        hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """

        st.markdown(hide_menu_style, unsafe_allow_html=True)