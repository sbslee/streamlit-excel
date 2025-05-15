import streamlit as st
import pandas as pd
import numpy as np

class Table:
    def __init__(self, df, key, mapper=None):
        self.df = self.preprocess(df)
        self.key = key
        self.data = {}
        self._view_cache = None
        self.mapper = mapper
        self.selected_filter = None

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

    def _get_label(self, column):
        if self.mapper is None:
            return column
        if self.mapper and column in self.mapper:
            return self.mapper[column]
        else:
            return column

    @st.cache_data()
    def get_unique(_self, series: pd.Series):
        return series.unique()

    @st.dialog("Categorical Filter")
    def _add_categorical_filter(self, column):
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

        with st.form(f"{self.key}_{column}", border=False):
            clicked_apply_filter = st.form_submit_button(label="Apply Filter", use_container_width=True)
            clicked_reset_filter = st.form_submit_button("Reset Filter", use_container_width=True)
            clicked_select_all = st.form_submit_button("Select All", use_container_width=True)
            selected_options = st.multiselect(
                "Options",
                label_visibility="collapsed",
                options=displayed_options,
                default=self.data[column]["selected_options"] if self.data[column]["selected_options"] else displayed_options if self.data[column]["select_all_state"] else None,
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

    @st.dialog("Datetime Filter")
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

    def show_filter_widget(self, label, columns, label_visibility="visible"):
        selected_filter = st.pills(
            label=label,
            options=["Reset All Filters"] + columns,
            default=None,
            format_func=self._get_label,
            selection_mode="single",
            label_visibility=label_visibility,
            key=f"{self.key}_filters",
        )
        if selected_filter is not None:
            if self.selected_filter is None or self.selected_filter != selected_filter:
                self.selected_filter = selected_filter
                if selected_filter == "Reset All Filters":
                    self.data = {}
                    self.reset_cache()
                elif self.df[selected_filter].dtype == "string":
                    self._add_categorical_filter(selected_filter)
                elif self.df[selected_filter].dtype == "datetime64[ns]":
                    self._add_datetime_filter(selected_filter)
                else:
                    st.warning(f"Column {selected_filter} has unsupported data type {self.df[selected_filter].dtype}.")

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
