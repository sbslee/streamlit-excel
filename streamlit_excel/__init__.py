import streamlit as st

class Table:
    def __init__(self, df):
        self.df = df
        self.filters = {}

    def add_filter(self, column):
        st.markdown("""
            <style>
                .stCheckbox {
                    margin-bottom: -20px;
                }
            </style>
        """, unsafe_allow_html=True)
        with st.form(column):
            with st.container(height=200):
                states = {}
                for option in self.df[column].unique():
                    states[option] = st.checkbox(option, value=True)
            options = [option for option, selected in states.items() if selected]
            applied = st.form_submit_button(label="Apply Filter")
            if applied and options:
                self.filters[column] = options
            elif applied and not options:
                st.warning("Please select at least one option.")

    def show_filter_panel(self, columns):
        with st.sidebar:
            with st.container():
                for column in columns:
                    self.add_filter(column)

    def view(self):
        df = self.df.copy()
        for column, options in self.filters.items():
            if column in df.columns:
                df = df[df[column].isin(options)]
        return df
