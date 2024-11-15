import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

st.markdown("Análisis de litro por kg")
path = Path("data/datos.xlsx")
df = pd.read_excel(path,sheet_name="LtKg", skiprows=2)
#df = pd.read_excel(path, sheet_name="LtKg", header=[0, 1, 2])
df.columns = ['_'.join(col).strip() for col in df.columns.values]
st.dataframe(df, hide_index=True)
df_melted = df.melt(
    id_vars=['Year', 'Industry', 'Sector'],
    var_name='Country_VolumeType',
    value_name='Volume'
)
df_melted[['Country', 'VolumeType']] = df_melted['Country_VolumeType'].str.split('_', expand=True)
df_melted = df_melted.drop(columns=['Country_VolumeType'])


st.markdown("Análisis de litro por kg")
st.dataframe(df_melted, hide_index=True)