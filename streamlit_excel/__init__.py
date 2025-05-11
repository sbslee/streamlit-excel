import streamlit as st
import pandas as pd
import numpy as np

class Table:
    def __init__(self, df, key):
        self.df = df
        self.key = key
        self.data = {}

    def _add_categorical_filter(self, column, max_displayed_options=50):
        if column not in self.data:
            self.data[column] = {
                "type": "categorical",
                "select_all_state": True,
                "selected_options": [],
            }

        displayed_options = self.view[column].unique()

        with st.popover(column, use_container_width=True):
            query = st.text_input(
                "Search",
                placeholder="Search",
                label_visibility="collapsed",
                key=f"{self.key}_{column}",
            )

            if query is not None:
                displayed_options = [option for option in displayed_options if query.lower() in option.lower()]

            with st.form(f"{self.key}_{column}", border=False):
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
                        option_states[option] = st.checkbox(
                            option,
                            value=self.data[column]["select_all_state"],
                        )
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
                    self.data.pop(column)
                    st.rerun()

    def _add_datetime_filter(self, column):
        if column not in self.data:
            self.data[column] = {
                "type": "datetime",
                "subtype": None,
            }

        with st.popover(column, use_container_width=True):
            tab1, tab2 = st.tabs(["Calendar", "Selection"])
            with tab1:
                with st.form(f"{self.key}_{column}_calendar", border=False):
                    min_date = self.view[column].min()
                    max_date = self.view[column].max()
                    selected_range = st.date_input(
                        "Calendar",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        label_visibility="collapsed",
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        clicked_apply_filter = st.form_submit_button(label="Apply Filter")
                    with col2:
                        clicked_reset_filter = st.form_submit_button("Reset Filter")
                    if clicked_apply_filter:
                        if selected_range:
                            self.data[column]["subtype"] = "calendar"
                            self.data[column]["selected_range"] = selected_range
                            st.rerun()
                        else:
                            st.warning("Please select a date range.")
                    elif clicked_reset_filter:
                        self.data.pop(column)
                        st.rerun()
            with tab2:
                with st.form(f"{self.key}_{column}_selection", border=False):
                    observed_years = np.sort(self.view[column].dt.year.unique())
                    observed_months = np.sort(self.view[column].dt.month.unique())
                    selected_years = st.multiselect(
                        "Years",
                        options=observed_years,
                        default=observed_years,
                        label_visibility="collapsed",
                    )
                    selected_months = st.multiselect(
                        "Months",
                        options=observed_months,
                        default=observed_months,
                        label_visibility="collapsed",
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        clicked_apply_filter = st.form_submit_button(label="Apply Filter")
                    with col2:
                        clicked_reset_filter = st.form_submit_button("Reset Filter")
                    if clicked_apply_filter:
                        if selected_years:
                            self.data[column]["subtype"] = "selection"
                            self.data[column]["selected_years"] = selected_years
                            self.data[column]["selected_months"] = selected_months
                            st.rerun()
                        else:
                            st.warning("Please select at least one year.")
                    elif clicked_reset_filter:
                        self.data.pop(column)
                        st.rerun()

    def show_filter_panel(self, label, columns):
        with st.sidebar:
            with st.expander(label):
                if st.button("Reset All Filters", key=f"{self.key}_{label}"):
                    self.data = {}
                for column in columns:
                    if self.df[column].dtype == "object":
                        self._add_categorical_filter(column)
                    elif self.df[column].dtype == "datetime64[ns]":
                        self._add_datetime_filter(column)
                    else:
                        st.warning(f"Column {column} has unsupported data type {self.df[column].dtype}.")

    @property
    def view(self):
        df = self.df.copy()
        for column, data in self.data.items():
            if data["type"] == "categorical":
                if data["selected_options"]:
                    df = df[df[column].isin(data["selected_options"])]
            elif data["type"] == "datetime":
                if data["subtype"] == "calendar":
                    if data["selected_range"]:
                        start = pd.to_datetime(data["selected_range"][0])
                        end = pd.to_datetime(data["selected_range"][1])
                        df = df[
                            (df[column] >= start) & (df[column] <= end)
                        ]
                elif data["subtype"] == "selection":
                    if data["selected_years"]:
                        df = df[df[column].dt.year.isin(data["selected_years"])]
                        if data["selected_months"]:
                            df = df[df[column].dt.month.isin(data["selected_months"])]
        return df
