import pandas as pd
import streamlit as st
from pathlib import Path
from Ventas import convert_df

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


# Filtrado por métricas seleccionadas
metricas_seleccionadas = st.selectbox("Selecciona la métrica para analizar:", df["Metric"].unique())
df_metric = filtered_df[filtered_df["Metric"] == metricas_seleccionadas]

# Gráfico de líneas por país
line_chart_data = df_metric.pivot_table(index="Year", columns="Country", values="Value", aggfunc="sum")

# Mostrar gráfico de líneas
st.subheader(f"Evolución de la métrica '{metricas_seleccionadas}' por País")
st.line_chart(line_chart_data)


# Filtrado por país y sector
df_bar = filtered_df.groupby(['Country', 'Sector'])['Value'].sum().reset_index()

# Gráfico de barras
st.subheader(f"Comparativa de métricas por País y Sector")
st.bar_chart(df_bar.set_index(['Country', 'Sector'])['Value'])

# Filtrado por marcas
df_area = filtered_df.groupby(['Year', 'Brand'])['Value'].sum().reset_index()

# Gráfico de área para visualizar tendencias acumuladas por marca
st.subheader(f"Tendencias acumuladas de métricas por Marca")
st.area_chart(df_area.set_index(['Year', 'Brand'])['Value'])
csv = convert_df(df)

st.download_button(
    label="Descarga tus datos como CSV",
    data=csv,
    file_name="large_df.csv",
    mime="text/csv",
)