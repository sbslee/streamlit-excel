import streamlit as st
import pandas as pd
import numpy as np

class Table:
    def __init__(self, df, key):
        self.df = self.preprocess(df)
        self.key = key
        self.data = {}
        self._view_cache = None

    @staticmethod
    def preprocess(df):
        df = df.copy()
        for column in df.select_dtypes(include="object").columns:
            df[column] = df[column].astype("string")
        for col in df.select_dtypes(include="datetime64[ns]").columns:
            df[col + "_year"]  = df[col].dt.year.astype("int16")
            df[col + "_month"] = df[col].dt.month.astype("int8")
            df[col + "_day"] = df[col].dt.day.astype("int8")
        return df

    def reset_cache(self):
        self._view_cache = None
        st.rerun()

    @st.cache_data()
    def get_unique(_self, series: pd.Series):
        return series.unique()

    @st.cache_data()
    def get_min_max(_self, series: pd.Series):
        return series.min(), series.max()

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
                "select_all_state": False,
                "selected_years": [],
                "selected_months": [],
                "selected_days": [],
            }

        if self.data[column]["selected_years"] or self.data[column]["selected_months"] or self.data[column]["selected_days"]:
            icon = ":material/filter_alt:"
        else:
            icon = None

        with st.popover(column, use_container_width=True, icon=icon):
            tab1, tab2 = st.tabs(["Calendar", "Selection"])
            with tab1:
                with st.form(f"{self.key}_{column}_calendar", border=False):
                    clicked_apply_filter = st.form_submit_button(label="Apply Filter", use_container_width=True)
                    clicked_reset_filter = st.form_submit_button("Reset Filter", use_container_width=True)
                    clicked_select_all = st.form_submit_button("Select All", use_container_width=True)
                    min_date, max_date = self.get_min_max(self.view[column])
                    selected_range = st.date_input(
                        "Calendar",
                        value=(min_date, max_date) if self.data[column]["select_all_state"] else [],
                        min_value=min_date,
                        max_value=max_date,
                        label_visibility="collapsed",
                    )
                    if clicked_apply_filter:
                        if selected_range:
                            selected_range = pd.date_range(
                                start=pd.to_datetime(selected_range[0]),
                                end=pd.to_datetime(selected_range[1])
                            )
                            self.data[column]["selected_years"] = selected_range.year.unique().to_list()
                            self.data[column]["selected_months"] = selected_range.month.unique().to_list()
                            self.data[column]["selected_days"] = selected_range.day.unique().to_list()
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
                    observed_years = np.sort(self.get_unique(self.view[f"{column}_year"]))
                    observed_months = np.sort(self.get_unique(self.view[f"{column}_month"]))
                    observed_days = np.sort(self.get_unique(self.view[f"{column}_day"]))
                    selected_years = st.multiselect(
                        "Years",
                        options=observed_years,
                        default=self.data[column]["selected_years"] if self.data[column]["selected_years"] else observed_years if self.data[column]["select_all_state"] else None,
                        placeholder="YYYY",
                        label_visibility="collapsed",
                    )
                    selected_months = st.multiselect(
                        "Months",
                        options=observed_months,
                        default=self.data[column]["selected_months"] if self.data[column]["selected_months"] else observed_months if self.data[column]["select_all_state"] else None,
                        placeholder="MM",
                        label_visibility="collapsed",
                    )
                    print(self.data[column]["selected_days"], observed_days)
                    selected_days = st.multiselect(
                        "Days",
                        options=observed_days,
                        default=self.data[column]["selected_days"] if self.data[column]["selected_days"] else observed_days if self.data[column]["select_all_state"] else None,
                        placeholder="DD",
                        label_visibility="collapsed",
                    )
                    if clicked_apply_filter:
                        if selected_years or selected_months or selected_days:
                            self.data[column]["selected_years"] = selected_years
                            self.data[column]["selected_months"] = selected_months
                            self.data[column]["selected_days"] = selected_days
                            self.reset_cache()
                        else:
                            st.warning("Please select at least one option.")
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
                targets = st.columns(2)
                for i, column in enumerate(columns):
                    with targets[i % 2]:
                        if self.df[column].dtype == "string":
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
                if data["selected_years"]:
                    mask &= self.df[f"{column}_year"].isin(data["selected_years"])
                if data["selected_months"]:
                    mask &= self.df[f"{column}_month"].isin(data["selected_months"])
                if data["selected_days"]:
                    mask &= self.df[f"{column}_day"].isin(data["selected_days"])
        self._view_cache = self.df.loc[mask]
        return self._view_cache
