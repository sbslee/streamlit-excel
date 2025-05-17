Welcome to the `streamlit-excel` package!

This package provides a Streamlit component that enables users to filter large 
datasets (e.g., over 100,000 rows) through an Excel-like interface. It allows 
for interactive filtering directly within a Streamlit app. Designed for ease 
of use and seamless integration, this component is ideal for data scientists 
and developers building interactive visualizations.

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