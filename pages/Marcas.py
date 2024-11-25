import pandas as pd
import streamlit as st
from pathlib import Path
from Ventas import convert_df
import plotly.express as px


st.set_page_config(page_title="Tablero de análisis de marca", layout="centered")

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
    
    # Opciones de filtros
    year_options = ["All"] + sorted(df["Year"].astype(str).unique())
    sector_options = ["All"] + sorted(df["Sector"].unique())
    segment_options = ["All"] + sorted(df["Segment"].unique())
    category_options = ["All"] + sorted(df["Category"].unique())
    trademark_owner_options = ["All"] + sorted(df["Trademark Owner"].unique())
    brand_options = ["All"] + sorted(df["Brand"].unique())
    
    # Valores por defecto
    default_country = ["All"]
    default_year = ["All"]
    default_sector = ["All"]
    default_segment = ["All"]
    default_category = ["All"]
    default_trademark_owner = ["All"]
    default_brand = ["All"]

    # Filtros
    countries = st.multiselect("País", options=["All"] + list(df["Country"].unique()), default=default_country)
    sectors = st.multiselect("Sector", options=sector_options, default=default_sector)
    segments = st.multiselect("Segmento", options=segment_options, default=default_segment)
    categories = st.multiselect("Categoría", options=category_options, default=default_category)
    trademark_owners = st.multiselect("Propietario de Marca", options=trademark_owner_options, default=default_trademark_owner)
    brands = st.multiselect("Marca", options=brand_options, default=default_brand)
    years = st.multiselect("Año", options=year_options, default=default_year)

# Aplicar filtros
filtered_df = df[
    (df["Country"].isin(countries) | ("All" in countries)) &
    (df["Sector"].isin(sectors) | ("All" in sectors)) &
    (df["Segment"].isin(segments) | ("All" in segments)) &
    (df["Category"].isin(categories) | ("All" in categories)) &
    (df["Trademark Owner"].isin(trademark_owners) | ("All" in trademark_owners)) &
    (df["Brand"].isin(brands) | ("All" in brands)) &
    (df["Year"].astype(str).isin(years) | ("All" in years))
]


csv = convert_df(filtered_df)

st.download_button(
    label="Descarga tus datos como CSV",
    data=csv,
    file_name="large_df.csv",
    mime="text/csv",
)


total_unidades = filtered_df["Value"].count()
ventas_totales = filtered_df["Value"].sum()


col1, col2 = st.columns([1, 2])

# Columna 1: Total de unidades vendidas
with col1:
    st.metric("Unidades Vendidas", f"{total_unidades:,}")

# Columna 2: Ventas Totales
with col2:
    st.metric("Ventas Totales", f"${ventas_totales:,.2f}")




# Gráfico de barras apiladas por Sector y Segmento
stacked_bar_sector_segment = px.bar(
    filtered_df.groupby(['Sector', 'Segment'])['Value'].sum().reset_index(),
    x="Sector",
    y="Value",
    color="Segment",
    title="Distribución de Ventas por Sector y Segmento",
    labels={"Value": "Ventas", "Sector": "Sector", "Segment": "Segmento"}
)
st.plotly_chart(stacked_bar_sector_segment)


bar_owner_brand = px.bar(
    filtered_df.groupby(['Trademark Owner', 'Brand'])['Value'].sum().reset_index(),
    x="Trademark Owner",
    y="Value",
    color="Brand",
    title="Ventas por Propietario de Marca y Marca",
    labels={"Value": "Ventas", "Trademark Owner": "Propietario de Marca", "Brand": "Marca"}
)
st.plotly_chart(bar_owner_brand)

# Histograma de Ventas por Segmento
histogram_segment = px.histogram(
    filtered_df,
    x="Value",
    color="Segment",
    nbins=30,
    title="Distribución de Ventas por Segmento",
    labels={"Value": "Ventas", "Segment": "Segmento"}
)
st.plotly_chart(histogram_segment)
# Gráfico de barras por Categoría y Propietario de Marca
bar_category_owner = px.bar(
    filtered_df.groupby(['Category', 'Trademark Owner'])['Value'].sum().reset_index(),
    x="Category",
    y="Value",
    color="Trademark Owner",
    title="Ventas por Categoría y Propietario de Marca",
    labels={"Value": "Ventas", "Category": "Categoría", "Trademark Owner": "Propietario de Marca"}
)
st.plotly_chart(bar_category_owner)
