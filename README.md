**Police SecureCheck – Traffic Stops Data Dashboard

This project is an interactive Streamlit web application that visualizes and analyzes traffic stops data.
It helps users filter data by various factors like stop date, time, driver age, race, vehicle number, and more — and predicts the likely violation and outcome based on selected filters.

Required Libraries:
Pandas,SQLALchemy, Streamlit

How it works:
Installed the required libraries

Loaded the CSV file and converted it into a DataFrame

Cleaned the DataFrame using pandas (handled NaN values, performed data type conversions)

Created a connection with PostgreSQL database

Executed SQL queries directly from VS Code and loaded the resulting DataFrames into Streamlit

In Streamlit:

Built a summary report

Added filters to predict likely violations and outcomes

Displayed a real-time interactive DataFrame

Created vehicle number–based summary reports

Showed advanced insights based on custom SQL queries

The .py file was run using:
streamlit run your_script_name.py to launch the Streamlit web application.







