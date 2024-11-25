import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px
from Ventas import convert_df


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
df["Value"] = df["Value"].replace("-", 0).astype(float)


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
        sectors = st.multiselect("Sector", options=["All"] + list(df["Sector"].unique()), default=default_sector)
        industries = st.multiselect("Industria", options=["All"] + list(df["Industry"].unique()), default=default_industry)
        years = st.multiselect("Año", options=year_options, default=default_year)
        categories = st.multiselect("Sector", options=["All"] + list(df["Category"].unique()), default=default_country)
        pack_material = st.multiselect("Pack Material", options=["All"] + list(df["Pack_Material"].unique()), default=default_industry)
        pack_type =  st.multiselect("Pack Type", options=["All"] + list(df["Pack_Type"].unique()), default=default_industry)
    # Aplicar filtros
        filtered_df = df[
        (df["Country"].isin(countries) | ("All" in countries)) &
        (df["Sector"].isin(sectors) | ("All" in sectors)) &
        (df["Industry"].isin(industries) | ("All" in industries)) &
        (df["Year"].astype(str).isin(years) | ("All" in years)) &
        (df["Category"].astype(str).isin(categories) | ("All" in categories)) &
        (df["Pack_Material"].astype(str).isin(pack_material) | ("All" in pack_material)) &
        (df["Pack_Type"].astype(str).isin(pack_type) | ("All" in pack_type))
    ]
st.dataframe(filtered_df, hide_index=True)
csv = convert_df(filtered_df)

st.download_button(
    label="Descarga tus datos filtrados como CSV",
    data=csv,
    file_name="large_df.csv",
    mime="text/csv",
)
df_sector = filtered_df.groupby(['Sector', 'Industry'])['Value'].sum().reset_index()

st.subheader("Distribución por Sector")
fig_sector = px.bar(
    df_sector,
    x="Sector",
    y="Value",
    color="Industry",
    title="Distribución por Sector e Industria",
    labels={"Value": "Value", "Sector": "Sector"}
)
st.plotly_chart(fig_sector, use_container_width=True)

df_country = filtered_df.groupby(['Country', 'Pack_Material'])['Value'].sum().reset_index()

st.subheader("Comparativa por País y Material de Empaque")
fig_country = px.bar(
    df_country,
    x="Country",
    y="Value",
    color="Pack_Material",
    title="Comparativa por País y Material de Empaque",
    labels={"Value": "Value", "Country": "Country"},
    barmode="stack"  # Cambia a "group" si prefieres barras agrupadas
)
st.plotly_chart(fig_country, use_container_width=True)
df_time = filtered_df.groupby(['Year', 'Country'])['Value'].sum().reset_index()

st.subheader("Evolución Temporal por País")
fig_time = px.line(
    df_time,
    x="Year",
    y="Value",
    color="Country",
    title="Evolución Temporal por País",
    markers=True,
    labels={"Value": "Value", "Year": "Year"}
)
st.plotly_chart(fig_time, use_container_width=True)
df_material = filtered_df.groupby('Pack_Material')['Value'].sum().reset_index()

st.subheader("Distribución por Material de Empaque")
fig_material = px.pie(
    df_material,
    names="Pack_Material",
    values="Value",
    title="Distribución por Material de Empaque",
    hole=0.3  # Para hacer un gráfico de dona
)
st.plotly_chart(fig_material, use_container_width=True)
