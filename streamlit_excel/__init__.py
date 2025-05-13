import streamlit as st
import pandas as pd
import numpy as np

class Table:
    def __init__(self, df, key):
        self.df = df
        self.key = key
        self.data = {}
        self._view_cache = None

    def reset_cache(self):
        self._view_cache = None
        st.rerun()

    @st.cache_data()
    def get_unique(_self, series: pd.Series):
        return series.unique()

    def _add_categorical_filter(self, column, max_displayed_options=50):
        if column not in self.data:
            self.data[column] = {
                "type": "categorical",
                "select_all_state": False,
                "selected_options": [],
            }

        displayed_options = self.get_unique(self.view[column])

        if not self.data[column]["selected_options"]:
            icon = None
        else:
            icon = ":material/filter_alt:"

        with st.popover(column, use_container_width=True, icon=icon):
            with st.form(f"{self.key}_{column}", border=False):
                clicked_apply_filter = st.form_submit_button(label="Apply Filter", use_container_width=True)
                clicked_reset_filter = st.form_submit_button("Reset Filter", use_container_width=True)
                clicked_select_all = st.form_submit_button("Select All", use_container_width=True)
                selected_options = st.multiselect(
                    "Options",
                    label_visibility="collapsed",
                    options=displayed_options,
                    default=displayed_options if self.data[column]["select_all_state"] else None,
                )
                if clicked_apply_filter and not selected_options:
                    st.warning("Please select at least one option.")
                elif clicked_apply_filter and selected_options:
                    self.data[column]["selected_options"] = selected_options
                    self.reset_cache()
                elif clicked_select_all:
                    self.data[column]["select_all_state"] = not self.data[column]["select_all_state"]
                    st.rerun()
                elif clicked_reset_filter:
                    self.data.pop(column)
                    self.reset_cache()

    def _add_datetime_filter(self, column):
        if column not in self.data:
            self.data[column] = {
                "type": "datetime",
                "subtype": None,
                "select_all_state": False,
            }

        if self.data[column]["subtype"] is None:
            icon = None
        else:
            icon = ":material/filter_alt:"

        with st.popover(column, use_container_width=True, icon=icon):
            tab1, tab2 = st.tabs(["Calendar", "Selection"])
            with tab1:
                with st.form(f"{self.key}_{column}_calendar", border=False):
                    clicked_apply_filter = st.form_submit_button(label="Apply Filter", use_container_width=True)
                    clicked_reset_filter = st.form_submit_button("Reset Filter", use_container_width=True)
                    clicked_select_all = st.form_submit_button("Select All", use_container_width=True)
                    min_date = self.view[column].min()
                    max_date = self.view[column].max()
                    selected_range = st.date_input(
                        "Calendar",
                        value=(min_date, max_date) if self.data[column]["select_all_state"] else None,
                        min_value=min_date,
                        max_value=max_date,
                        label_visibility="collapsed",
                    )
                    if clicked_apply_filter:
                        if selected_range:
                            self.data[column]["subtype"] = "calendar"
                            self.data[column]["selected_range"] = selected_range
                            self.reset_cache()
                        else:
                            st.warning("Please select a date range.")
                    elif clicked_reset_filter:
                        self.data.pop(column)
                        self.reset_cache()
                    elif clicked_select_all:
                        self.data[column]["select_all_state"] = not self.data[column]["select_all_state"]
                        st.rerun()
            with tab2:
                with st.form(f"{self.key}_{column}_selection", border=False):
                    clicked_apply_filter = st.form_submit_button(label="Apply Filter", use_container_width=True)
                    clicked_reset_filter = st.form_submit_button("Reset Filter", use_container_width=True)
                    clicked_select_all = st.form_submit_button("Select All", use_container_width=True)
                    observed_years = np.sort(self.get_unique(self.view[column].dt.year))
                    observed_months = np.sort(self.get_unique(self.view[column].dt.month))
                    selected_years = st.multiselect(
                        "Years",
                        options=observed_years,
                        default=observed_years if self.data[column]["select_all_state"] else None,
                        label_visibility="collapsed",
                    )
                    selected_months = st.multiselect(
                        "Months",
                        options=observed_months,
                        default=observed_months if self.data[column]["select_all_state"] else None,
                        label_visibility="collapsed",
                    )
                    if clicked_apply_filter:
                        if selected_years:
                            self.data[column]["subtype"] = "selection"
                            self.data[column]["selected_years"] = selected_years
                            self.data[column]["selected_months"] = selected_months
                            self.reset_cache()
                        else:
                            st.warning("Please select at least one year.")
                    elif clicked_reset_filter:
                        self.data.pop(column)
                        self.reset_cache()
                    elif clicked_select_all:
                        self.data[column]["select_all_state"] = not self.data[column]["select_all_state"]
                        st.rerun()

    def show_filter_panel(self, label, columns):
        with st.sidebar:
            with st.expander(label):
                if st.button("Reset All Filters", key=f"{self.key}_{label}"):
                    self.data = {}
                    self.reset_cache()
                cols = st.columns(2)
                for i, column in enumerate(columns):
                    with cols[i % 2]:
                        if self.df[column].dtype == "object":
                            self._add_categorical_filter(column)
                        elif self.df[column].dtype == "datetime64[ns]":
                            self._add_datetime_filter(column)
                        else:
                            st.warning(f"Column {column} has unsupported data type {self.df[column].dtype}.")

    @property
    def view(self):
        if self._view_cache is not None:
            return self._view_cache
        mask = pd.Series(True, index=self.df.index)
        for column, data in self.data.items():
            if data["type"] == "categorical":
                if data["selected_options"]:
                    mask &= self.df[column].isin(data["selected_options"])
            elif data["type"] == "datetime":
                if data["subtype"] == "calendar":
                    if data["selected_range"]:
                        start = pd.to_datetime(data["selected_range"][0])
                        end = pd.to_datetime(data["selected_range"][1])
                        mask &= (self.df[column] >= start) & (self.df[column] <= end)
                elif data["subtype"] == "selection":
                    if data["selected_years"]:
                        mask &= self.df[column].dt.year.isin(data["selected_years"])
                        if data["selected_months"]:
                            mask &= self.df[column].dt.month.isin(data["selected_months"])
        self._view_cache = self.df.loc[mask]
        return self._view_cache
