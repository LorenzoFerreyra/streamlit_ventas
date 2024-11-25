import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px

st.set_page_config(page_title="Tablero de análisis por Lt/Kg", layout="centered")

path = Path("data/datos.xlsx")

df = pd.read_excel(path, sheet_name="Marcas", header=None)

# Extract the first three rows for the header
header_rows = df.iloc[:3]

# Fill forward to deal with merged cells
header_rows = header_rows.fillna(method="ffill", axis=1)
print(header_rows)
# Combine rows to create a single header
columns = header_rows.apply(lambda x: "_".join(x.dropna().astype(str)), axis=0)
# Drop the first three rows (headers) from the data
df = df.iloc[6:]

# Assign the constructed header
df.columns = columns

# Melt the DataFrame to long format
melted_df = df.melt(
    id_vars=['Year','Sector','Segment','Category','Trademark Owner','Brand'],
    var_name="Country_Metric",
    value_name="Value",
)
st.dataframe(melted_df,  hide_index=True)
# Split 'Country_Metric' into 'Country' and 'Metric'
melted_df[["Country", "Metric"]] = melted_df["Country_Metric"].str.rsplit("_", n=1, expand=True)
# Asegurarnos de que los valores en Year, Industry y Sector se propaguen hacia abajo
melted_df[['Year','Sector','Segment','Category','Trademark Owner','Brand']] = melted_df[['Year','Sector','Segment','Category','Trademark Owner','Brand']].fillna(method='ffill')

# Drop the combined column
df = melted_df.drop(columns=["Country_Metric"])

st.title("Análisis de performance de marcas")
st.dataframe(df,  hide_index=True)