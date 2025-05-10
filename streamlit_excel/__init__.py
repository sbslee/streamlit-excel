import streamlit as st

class Table:
    def __init__(self, df):
        self.df = df
        self.filters = {}
        self.select_all = {}

    def add_filter(self, column):
        st.markdown("""
            <style>
                .stCheckbox {
                    margin-bottom: -20px;
                }
            </style>
        """, unsafe_allow_html=True)

        if column not in self.select_all:
            self.select_all[column] = True

        if st.button("Select All"):
            self.select_all[column] = not self.select_all[column]

        with st.form(column, border=False):
            with st.container(height=200):
                states = {}
                for option in self.df[column].unique():
                    states[option] = st.checkbox(option, value=self.select_all[column])
            options = [option for option, selected in states.items() if selected]
            applied = st.form_submit_button(label="Apply Filter")
            if applied and options:
                self.filters[column] = options
            elif applied and not options:
                st.warning("Please select at least one option.")

    def show_filter_panel(self, columns):
        with st.sidebar:
            with st.container(border=True):
                for column in columns:
                    self.add_filter(column)

    def view(self):
        df = self.df.copy()
        for column, options in self.filters.items():
            if column in df.columns:
                df = df[df[column].isin(options)]
        return df
