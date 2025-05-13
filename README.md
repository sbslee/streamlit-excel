# Installation

```sh
$ pip install streamlit-excel streamlit pandas
```

# Usage

```python
import streamlit as st
import streamlit_excel
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

if "example_table" not in st.session_state:
    df = pd.DataFrame({
        "Name": np.random.choice(["Emily Johnson", "Michael Smith"], 10),
        "City": np.random.choice(["Kyoto", "Cape Town", "Vancouver"], 10),
        "Color": np.random.choice(['Red', 'Green', 'Blue'], 10),
        "Start": [datetime(2023, 1, 1) + timedelta(days=np.random.randint(30)) for _ in range(10)],
        "End": [datetime(2023, 1, 15) + timedelta(days=np.random.randint(30)) for _ in range(10)],
    })
    st.session_state.example_table = streamlit_excel.Table(df, "example_table")

st.session_state.example_table.show_filter_panel("Example Table", ["Name", "City", "Color", "Start", "End"])
st.dataframe(st.session_state.example_table.view)
```