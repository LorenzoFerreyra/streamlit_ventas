import pandas as pd
import streamlit as st
from pathlib import Path
from Ventas import convert_df
import plotly.express as px


st.set_page_config(page_title="Tablero de análisis por Lt/Kg", layout="centered")

path = Path("data/datos.xlsx")

df = pd.read_excel(path, sheet_name="Marcas", header=None)

# Extract the first three rows for the header
header_rows = df.iloc[:3]
print(header_rows)
# Fill forward to deal with merged cells
header_rows = header_rows.fillna(method="ffill", axis=1)
print(header_rows)
# Combine rows to create a single header
columns = header_rows.apply(lambda x: "_".join(x.dropna().astype(str)), axis=0)

df = df.iloc[3:]

# Assign the constructed header
df.columns = columns

# Melt the DataFrame to long format
melted_df = df.melt(
    id_vars=['Year','Sector','Segment','Category','Trademark Owner','Brand'],
    var_name="Country_Metric",
    value_name="Value",
)

# Split 'Country_Metric' into 'Country' and 'Metric'
melted_df[["Country", "Metric"]] = melted_df["Country_Metric"].str.rsplit("_", n=1, expand=True)

melted_df[['Year','Sector','Segment','Category','Trademark Owner','Brand']] = melted_df[['Year','Sector','Segment','Category','Trademark Owner','Brand']].fillna(method='ffill')

# Drop the combined column
df = melted_df.drop(columns=["Country_Metric"])
df["Value"] = df["Value"].replace("-", 0).astype(float)
st.title("Análisis de performance de marcas")
st.dataframe(df,  hide_index=True)


with st.sidebar:
    st.header("Filtros")
    year_options = ["All"] + sorted(df["Year"].astype(str).unique())
    default_country = ["All"]
    default_year = ["All"]
    default_sector = ["All"]

    # Filtros
    countries = st.multiselect("País", options=["All"] + list(df["Country"].unique()), default=default_country)
    sectors = st.multiselect("Sector", options=["All"] + list(df["Sector"].unique()), default=default_country)
    years = st.multiselect("Año", options=year_options, default=default_year)

# Aplicar filtros
filtered_df = df[
    (df["Country"].isin(countries) | ("All" in countries)) &
    (df["Sector"].isin(sectors) | ("All" in sectors)) &
    (df["Year"].astype(str).isin(years) | ("All" in years))
]
# Tarjetas de KPI
st.subheader("KPIs Principales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"${filtered_df['Value'].sum():,.2f}")
col2.metric("Países", filtered_df["Country"].nunique())
col3.metric("Sectores", filtered_df["Sector"].nunique())
col4.metric("Marcas", filtered_df["Brand"].nunique())

# Visualizaciones
st.subheader("Gráficos")

# Gráfico 1: Ventas por Marca y País (Barras horizontales)
bar_chart = px.bar(
    filtered_df.groupby(['Country', 'Brand'])['Value'].sum().reset_index(),
    x="Value",
    y="Brand",
    color="Country",
    orientation="h",
    title="Ventas por Marca y País",
    labels={"Value": "Ventas", "Brand": "Marca", "Country": "País"}
)
st.plotly_chart(bar_chart)

# Gráfico 2: Distribución por Sector (Barras apiladas)
stacked_bar = px.bar(
    filtered_df.groupby(['Year', 'Sector'])['Value'].sum().reset_index(),
    x="Year",
    y="Value",
    color="Sector",
    title="Distribución de Ventas por Sector y Año",
    labels={"Value": "Ventas", "Year": "Año", "Sector": "Sector"}
)
st.plotly_chart(stacked_bar)

# Gráfico 3: Relación entre Sector y Métrica (Dispersión)
scatter_plot = px.scatter(
    filtered_df,
    x="Sector",
    y="Value",
    color="Metric",
    size="Value",
    title="Relación entre Sector y Métrica",
    labels={"Value": "Ventas", "Sector": "Sector", "Metric": "Métrica"},
    hover_data=["Country", "Brand"]
)
st.plotly_chart(scatter_plot)
csv = convert_df(filtered_df)

st.download_button(
    label="Descarga tus datos como CSV",
    data=csv,
    file_name="large_df.csv",
    mime="text/csv",
)