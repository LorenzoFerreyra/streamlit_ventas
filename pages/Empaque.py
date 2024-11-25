import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px

st.set_page_config(page_title="Tablero de análisis por empaque", layout="centered")

path = Path("data/datos.xlsx")

df = pd.read_excel(path, sheet_name="Empaque", header=None)


header_rows = df.iloc[:7]

# Fill forward to deal with merged cells
header_rows = header_rows.fillna(method="ffill", axis=1)

# Combine rows to create a single header
columns = header_rows.apply(lambda x: "_".join(x.dropna().astype(str)), axis=0)
# Drop the first seven rows (headers) from the data
df = df.iloc[7:]

# Assign the constructed header
df.columns = columns

# Melt the DataFrame to long format
melted_df = df.melt(
    id_vars=["Year", "Industry", "Sector","Category"],
    var_name="Country_Pack Material_Pack Type",
    value_name="Value",
)
processed_df = melted_df.copy()
    
    # Separar la columna combinada
split_cols = processed_df['Country_Pack Material_Pack Type'].str.extract(
        r'Country_Pack Material_Pack Type_(.+)_(.+)_(.+)_Volume'
    )
    
    # Asignar nombres a las nuevas columnas
split_cols.columns = ['Country', 'Pack_Material', 'Pack_Type']
    
    # Añadir las nuevas columnas al DataFrame
processed_df = pd.concat([processed_df, split_cols], axis=1)
    
    # Eliminar la columna original combinada
processed_df = processed_df.drop('Country_Pack Material_Pack Type', axis=1)
    
    # Reordenar las columnas
column_order = [
        'Year', 'Industry', 'Sector', 'Category',
        'Country', 'Pack_Material', 'Pack_Type', 'Value'
    ]
    
df = processed_df[column_order]
st.title("Análisis de métricas por empaque")
st.dataframe(df, hide_index=True)

# Filtros interactivos
with st.sidebar:
        st.header("Filtros")
        year_options = ["All"] + sorted(df["Year"].astype(str).unique())
        default_country = ["All"]
        default_industry = ["All"]
        default_year = ["All"]
        default_sector = ["All"]

        # Filtros
        countries = st.multiselect("País", options=["All"] + list(df["Country"].unique()), default=default_country)
        sectors = st.multiselect("Sector", options=["All"] + list(df["Sector"].unique()), default=default_country)
        industries = st.multiselect("Industria", options=["All"] + list(df["Industry"].unique()), default=default_industry)
        years = st.multiselect("Año", options=year_options, default=default_year)

    # Aplicar filtros
        filtered_df = df[
        (df["Country"].isin(countries) | ("All" in countries)) &
        (df["Sector"].isin(sectors) | ("All" in sectors)) &
        (df["Industry"].isin(industries) | ("All" in industries)) &
        (df["Year"].astype(str).isin(years) | ("All" in years))
    ]

# Gráfico 1: Distribución por Sector
st.subheader("Distribución por Sector")
fig_sector = px.bar(
    filtered_df,
    x="Sector",
    y="Value",
    color="Industry",
    title="Distribución por Sector e Industria",
    labels={"Value": "Valor", "Sector": "Sector"},
)
st.plotly_chart(fig_sector)

# Gráfico 2: Comparativa por País
st.subheader("Comparativa por País")
fig_country = px.line(
    filtered_df,
    x="Country",
    y="Value",
    color="Industry",
    markers=True,
    title="Tendencia de Métricas por País",
    labels={"Value": "Valor", "Country": "País"},
)
st.plotly_chart(fig_country)

# Gráfico 3: Evolución en el tiempo
st.subheader("Evolución en el Tiempo")
time_df = df[
    (df["Country"].isin(countries) if countries else True)
]
fig_time = px.line(
    time_df,
    x="Year",
    y="Value",
    color="Country",
    title="Evolución Temporal por País",
    labels={"Value": "Valor", "Year": "Año"},
)
st.plotly_chart(fig_time)

