import streamlit as st

class Table:
    def __init__(self, df):
        self.df = df
        self.data = {}

    def _add_filter(self, column):
        st.markdown("""
            <style>
                .stCheckbox {
                    margin-bottom: -20px;
                }
            </style>
        """, unsafe_allow_html=True)

        if column not in self.data:
            self.data[column] = {
                "select_all_state": True,
                "selected_options": [],
                "frozen_options": [],
            }

        self.data[column]["frozen_options"] = list(self.view[column].unique())

        displayed_options = self.data[column]["frozen_options"][:]
        
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Select All", key=f"select_all_state_{column}"):
                self.data[column]["select_all_state"] = not self.data[column]["select_all_state"]
                
        with col2:
            query = st.text_input(
                "Search",
                placeholder="Search",
                label_visibility="collapsed",
                key=f"search_{column}",
            )

        if query is not None:
            displayed_options = [option for option in displayed_options if query.lower() in option.lower()]

        with st.form(column, border=False):
            with st.container(height=100, border=True):
                option_states = {}
                for option in displayed_options:
                    option_states[option] = st.checkbox(option, value=self.data[column]["select_all_state"])
            selected_options = [option for option, selected in option_states.items() if selected]
            filter_applied = st.form_submit_button(label="Apply Filter")
            if filter_applied and selected_options:
                self.data[column]["selected_options"] = selected_options
            elif filter_applied and not selected_options:
                st.warning("Please select at least one option.")

    def show_filter_panel(self, label, columns):
        with st.sidebar:
            with st.expander(label):
                with st.container():
                    if st.button("Reset Filters"):
                        self.data = {}
                    for column in columns:
                        self._add_filter(column)

    @property
    def view(self):
        df = self.df.copy()
        for column, data in self.data.items():
            if data["selected_options"]:
                df = df[df[column].isin(data["selected_options"])]
        return df
