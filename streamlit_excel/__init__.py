import streamlit as st

class Table:
    def __init__(self, df):
        self.df = df
        self.data = {}

    def _add_css(self):
        st.markdown("""
            <style>
                /* Reduce font size and internal div size */
                section[data-testid="stSidebar"] button > div {
                    font-size: 12px !important;
                    padding: 2px 8px !important;
                }

                /* Shrink the button height and spacing */
                section[data-testid="stSidebar"] button {
                    padding: 2px 8px !important;
                    height: auto !important;
                    min-height: 28px !important;
                }
                div[data-testid="stCheckbox"] > label {
                    transform: scale(0.75);
                    transform-origin: top left;
                    display: inline-flex;
                    align-items: center;
                }
                .stCheckbox {
                    margin-bottom: -25px;
                }
            </style>
        """, unsafe_allow_html=True)

    def _add_filter(self, column):
        self._add_css()

        if column not in self.data:
            self.data[column] = {
                "select_all_state": True,
                "selected_options": [],
            }

        displayed_options = self.view[column].unique()

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

            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_applied = st.form_submit_button(label="Apply")
            with col2:
                if st.form_submit_button("All"):
                    self.data[column]["select_all_state"] = not self.data[column]["select_all_state"]
                    st.rerun()
            with col3:
                if st.form_submit_button("Clear"):
                    self.data[column]["select_all_state"] = True
                    self.data[column]["selected_options"] = []
                    st.rerun()
            if filter_applied and selected_options:
                self.data[column]["selected_options"] = selected_options
                st.rerun()
            elif filter_applied and not selected_options:
                st.warning("Please select at least one option.")

    def show_filter_panel(self, label, columns):
        with st.sidebar:
            with st.expander(label):
                with st.container():
                    if st.button("Reset"):
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
