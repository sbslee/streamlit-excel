import streamlit as st
import pandas as pd
import numpy as np

class Table:
    """
    A class for managing and filtering tabular data in a Streamlit application.

    The `Table` class provides functionality to preprocess a pandas DataFrame, 
    apply categorical and datetime filters, and display a filtered view of the data. 
    It integrates with Streamlit to create interactive filter widgets and dialogs.

    Attributes:
        df (pd.DataFrame): The preprocessed DataFrame.
        key (str): A unique key for the table instance, used for Streamlit widgets.
        data (dict): A dictionary storing filter configurations for each column.
        mapper (dict): Optional mapping of column names to display labels.
        selected_filter (str): The currently selected filter column.
        _view_cache (pd.DataFrame): Cached view of the filtered DataFrame.
    """
    def __init__(self, df, key, mapper=None):
        self.df = self.preprocess(df)
        self.key = key
        self.data = {}
        self.mapper = mapper
        self.last_filter = None
        self.select_all = False
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
        """Resets the cached filtered view and triggers a Streamlit rerun."""
        self._view_cache = None
        st.rerun()

    def _format_func(self, option):
        """Formats the display label for filter options in the filter widget."""
        label = self._get_label(option)
        if option == "Reset All Filters":
            return label
        if option not in self.data:
            return label
        if self.data[option]["type"] == "categorical":
            if self.data[option]["selected_options"]:
                return f"{label} :material/filter_alt:"
            else:
                return label
        if self.data[option]["type"] == "datetime":
            if self.data[option]["selected_years"] or self.data[option]["selected_months"] or self.data[option]["selected_days"]:
                return f"{label} :material/filter_alt:"
            else:
                return label
        return label
    
    def _get_label(self, column):
        """Retrieves the display label for a column, using the mapper if provided."""
        if column == "Reset All Filters":
            return ":material/restart_alt:"
        if self.mapper is None:
            return column
        if self.mapper and column in self.mapper:
            return self.mapper[column]
        else:
            return column

    def _get_default_options(self, column, target, observed_options, select_all):
        if select_all:
            default_options = observed_options
        elif self.data[column][target]:
            default_options = self.data[column][target]
        else:
            default_options = None
        return default_options

    @st.cache_data()
    def get_unique(_self, series: pd.Series):
        """Returns the unique values of a pandas Series (cached by Streamlit)."""
        return series.unique()

    @st.dialog("Categorical Filter")
    def _add_categorical_filter(self, column, select_all=False):
        """Displays a dialog for applying a categorical filter to a column."""
        if column not in self.data:
            self.data[column] = {
                "type": "categorical",
                "selected_options": [],
            }

        observed_options = self.get_unique(self.view[column])

        with st.form(f"{self.key}_{column}", border=False):
            clicked_apply_filter = st.form_submit_button(label="Apply Filter", use_container_width=True)
            clicked_reset_filter = st.form_submit_button("Reset Filter", use_container_width=True)
            clicked_select_all = st.form_submit_button("Select All", use_container_width=True)
            selected_options = st.multiselect(
                "Options",
                label_visibility="collapsed",
                options=observed_options,
                default=self._get_default_options(column, "selected_options", observed_options, select_all),
            )
            if clicked_apply_filter and not selected_options:
                st.warning("Please select at least one option.")
            elif clicked_apply_filter and selected_options:
                self.data[column]["selected_options"] = selected_options
                self.reset_cache()
            elif clicked_reset_filter:
                self.data.pop(column)
                self.reset_cache()
            elif clicked_select_all:
                self.select_all = True
                st.rerun()

    @st.dialog("Datetime Filter")
    def _add_datetime_filter(self, column, select_all=False):
        """Displays a dialog for applying a datetime filter to a column."""
        if column not in self.data:
            self.data[column] = {
                "type": "datetime",
                "selected_years": [],
                "selected_months": [],
                "selected_days": [],
            }

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
                default=self._get_default_options(column, "selected_years", observed_years, select_all),
                placeholder="YYYY",
                label_visibility="collapsed",
            )
            selected_months = st.multiselect(
                "Months",
                options=observed_months,
                default=self._get_default_options(column, "selected_months", observed_months, select_all),
                placeholder="MM",
                label_visibility="collapsed",
            )
            selected_days = st.multiselect(
                "Days",
                options=observed_days,
                default=self._get_default_options(column, "selected_days", observed_days, select_all),
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
                self.select_all = True
                st.rerun()

    def show_filter_widget(self, label, columns, label_visibility="visible"):
        """Displays a filter widget for selecting and applying filters to columns."""

        if self.select_all:
            default = self.last_filter
        else:
            default = None

        selected_filter = st.pills(
            label=label,
            options=["Reset All Filters"] + columns,
            default=default,
            format_func=self._format_func,
            selection_mode="single",
            label_visibility=label_visibility,
            key=f"{self.key}_filters",
        )

        if selected_filter is None:
            self.last_filter = None
        elif self.last_filter is None or self.last_filter != selected_filter:
            self.last_filter = selected_filter
            if selected_filter == "Reset All Filters":
                self.data = {}
                self.reset_cache()
            elif self.df[selected_filter].dtype == "string":
                self._add_categorical_filter(selected_filter)
            elif self.df[selected_filter].dtype == "datetime64[ns]":
                self._add_datetime_filter(selected_filter)
            else:
                st.warning(f"Column {selected_filter} has unsupported data type {self.df[selected_filter].dtype}.")
        else:         
            self.last_filter = selected_filter
            if selected_filter == "Reset All Filters":
                self.data = {}
                self.reset_cache()
            elif self.df[selected_filter].dtype == "string":
                self._add_categorical_filter(selected_filter, select_all=True)
            elif self.df[selected_filter].dtype == "datetime64[ns]":
                self._add_datetime_filter(selected_filter, select_all=True)
            else:
                st.warning(f"Column {selected_filter} has unsupported data type {self.df[selected_filter].dtype}.")
            self.select_all = False

    @property
    def view(self):
        """Returns the filtered view of the DataFrame, applying all active filters."""
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
