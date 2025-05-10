from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()

exec(open("streamlit_excel/version.py").read())

setup(
    name="streamlit-excel",
    version=__version__,
    author='Seung-been "Steven" Lee',
    author_email="sbstevenlee@gmail.com",
    description="Build Excel-style filter panels for pandas DataFrames in Streamlit",
    url="https://github.com/sbslee/streamlit-excel",
    packages=find_packages(),
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown"
)