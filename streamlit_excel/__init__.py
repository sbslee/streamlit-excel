import streamlit as st

class Table:
    def __init__(self, df):
        self.df = df
        self.data = {}

    def _add_filter(self, column, max_displayed_options=50):
        if column not in self.data:
            self.data[column] = {
                "select_all_state": True,
                "selected_options": [],
            }

        displayed_options = self.view[column].unique()

        with st.popover(column, use_container_width=True):
            query = st.text_input(
                "Search",
                placeholder="Search",
                label_visibility="collapsed",
                key=f"search_{column}",
            )

            if query is not None:
                displayed_options = [option for option in displayed_options if query.lower() in option.lower()]

            with st.form(column, border=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    clicked_apply_filter = st.form_submit_button(label="Apply Filter")
                with col2:
                    clicked_select_all = st.form_submit_button("Select All")
                with col3:
                    clicked_reset_filter = st.form_submit_button("Reset Filter")
                option_states = {}
                with st.container(height=200):
                    for option in displayed_options[:max_displayed_options]:
                        option_states[option] = st.checkbox(option, value=self.data[column]["select_all_state"])
                if len(displayed_options) > max_displayed_options:
                    st.warning(f"Too many options to display. Showing first {max_displayed_options} options.")
                selected_options = [option for option, selected in option_states.items() if selected]
                if clicked_apply_filter and not selected_options:
                    st.warning("Please select at least one option.")
                elif clicked_apply_filter and selected_options:
                    self.data[column]["selected_options"] = selected_options
                    st.rerun()
                elif clicked_select_all:
                    self.data[column]["select_all_state"] = not self.data[column]["select_all_state"]
                    st.rerun()
                elif clicked_reset_filter:
                    self.data[column]["select_all_state"] = True
                    self.data[column]["selected_options"] = []
                    st.rerun()

    def show_filter_panel(self, label, columns):
        with st.sidebar:
            with st.expander(label):
                with st.container():
                    if st.button("Reset All Filters"):
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
