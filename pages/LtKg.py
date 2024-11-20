import pandas as pd
import streamlit as st
from pathlib import Path

path = Path("data/datos.xlsx")

df = pd.read_excel(path, sheet_name="LtKg", header=None)

# Extract the first three rows for the header
header_rows = df.iloc[:3]

# Fill forward to deal with merged cells
header_rows = header_rows.fillna(method="ffill", axis=1)

# Combine rows to create a single header
columns = header_rows.apply(lambda x: "_".join(x.dropna().astype(str)), axis=0)
# Drop the first three rows (headers) from the data
df = df.iloc[3:]

# Assign the constructed header
df.columns = columns

# Melt the DataFrame to long format
melted_df = df.melt(
    id_vars=["Year", "Industry", "Sector"],
    var_name="Country_Metric",
    value_name="Value",
)

# Split 'Country_Metric' into 'Country' and 'Metric'
melted_df[["Country", "Metric"]] = melted_df["Country_Metric"].str.rsplit("_", n=1, expand=True)
# Asegurarnos de que los valores en Year, Industry y Sector se propaguen hacia abajo
melted_df[['Year', 'Industry', 'Sector']] = melted_df[['Year', 'Industry', 'Sector']].fillna(method='ffill')

# Drop the combined column
melted_df = melted_df.drop(columns=["Country_Metric"])

st.dataframe(melted_df)
# Guardar el resultado a un archivo CSV
melted_df.to_csv("tabular_data.csv", index=False)
