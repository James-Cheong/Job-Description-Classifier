import streamlit as st
import pandas as pd

df = pd.read_csv('gov_jobs.csv')
df=df.iloc[:,0:5]
st.write("Here's our first attempt at using data to create a table:")
st.write(df.head())