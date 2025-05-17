[![PyPI version](https://badge.fury.io/py/streamlit-excel.svg)](https://badge.fury.io/py/streamlit-excel)

Welcome to the `streamlit-excel` package!

This package provides a Streamlit component for filtering large pandas 
DataFrames (e.g., over 100,000 rows) through an intuitive, Excel-like 
interface. It enables interactive filtering directly within a Streamlit app, 
allowing users to explore and refine data visually and efficiently.

Designed for simplicity and seamless integration, the component is ideal for 
data scientists and developers building interactive data visualizations.

# Key Features

- **Easy Integration**: Initialize the component with a Pandas DataFrame using the `Table` class and store it in the session state.
- **Flexible Filtering**: Use `Table.show_filter_widget` to render a filter widget for specific columns. The widget can be placed anywhere in the app, including the sidebar.
- **Dynamic Views**: Access the filtered DataFrame via the `Table.view` property.
- **Multiple Tables**: Support for multiple tables by creating separate `Table` instances with unique `key` parameters.
- **Custom Column Names**: Customize display names in the filter widget by passing a dictionary to the `mapper` parameter when creating the `Table` instance.

# Installation

```sh
$ pip install streamlit-excel streamlit pandas
```

# Usage

Below is a simple example demonstrating how to use the `streamlit-excel` 
package to create a filterable table in a Streamlit app. In this example, we 
generate a random dataset with 100,000 rows and 5 columns to showcase the 
package's scalability.

Save the following code to `app.py`:

```python
import streamlit as st
import streamlit_excel
import pandas as pd
import numpy as np
import random
from datetime import datetime

if "example_table" not in st.session_state:
    n = 100000
    df = pd.DataFrame({
        "Name": np.random.choice(["Emily Johnson", "Michael Smith", "Lena Corwin", "Talia Vexley", "Kai Renford"], n),
        "City": np.random.choice(["Kyoto", "Cape Town", "Vancouver", "New York City", "Paris"], n),
        "Color": np.random.choice(["Red", "Green", "Yellow", "Blue"], n),
        "Start": [datetime(random.randint(1999, 2022), random.randint(1, 12), random.randint(1, 28)) for _ in range(n)],
        "End": [datetime(random.randint(2023, 2025), random.randint(1, 12), random.randint(1, 28)) for _ in range(n)],
    })
    st.session_state.example_table = streamlit_excel.Table(df, "example_table")

st.session_state.example_table.show_filter_widget("Example Table", ["Name", "City", "Color", "Start", "End"])
st.dataframe(st.session_state.example_table.view)
st.dataframe(st.session_state.example_table.view.describe(include="all"))
```

Run the app:

```sh
$ streamlit run app.py
```