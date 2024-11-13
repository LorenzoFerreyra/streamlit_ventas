import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path


path = Path("data/datos.xlsx")
all_sheets = pd.read_excel(path, sheet_name=None, skiprows=2)

sheets_to_exclude = ["LtKg", "Empaque", "Marcas"]

df_list = []

for sheet_name, df in all_sheets.items():
    if sheet_name in sheets_to_exclude:
        continue
    
    # Verificar que el DataFrame tenga el número correcto de columnas
    if df.shape[1] >= 6:
        # Seleccionar solo las primeras 6 columnas y renombrarlas
        df = df.iloc[:, :6]
        df.columns = ['Industry', 'Sector', 'Category', 'Year', 'Value_M_USD', 'Growth_Percentage']
    else:
        print(f"Advertencia: La hoja {sheet_name} no tiene suficientes columnas.")
        continue
    
    # Rellena valores faltantes en 'Industry', 'Sector', y 'Category'
    df[['Industry', 'Sector', 'Category']] = df[['Industry', 'Sector', 'Category']].ffill()
    
    # Limpia y convierte 'Value_M_USD'
    df['Value_M_USD'] = df['Value_M_USD'].replace({',': '', '-': np.nan}, regex=True).astype(float)
    
    # Limpia y convierte 'Growth_Percentage'
    df['Growth_Percentage'] = df['Growth_Percentage'].astype(str).str.replace('%', '').replace('-', np.nan).astype(float)
    
    # Agrega la columna de país con el nombre de la hoja
    df['Country'] = sheet_name
    
    # Agrega el DataFrame procesado a la lista
    df_list.append(df)

# Concatena todos los DataFrames en uno solo
df = pd.concat(df_list, ignore_index=True)

st.title("Tablero de Análisis de Ventas")
st.dataframe(df, hide_index=True)

# Configurar título y descripción del tablero

st.markdown("Este tablero muestra los datos de ventas por industria, sector y categoría, y permite aplicar filtros interactivos.")

# Configurar filtros
country_options = ["All"] + list(df["Country"].unique())
industry_options = ["All"] + list(df["Industry"].unique())
year_options = ["All"] + sorted(df["Year"].unique())

country = st.sidebar.selectbox("País", country_options)
industry = st.sidebar.selectbox("Industria", industry_options)
year = st.sidebar.selectbox("Año", year_options)

# Apply filters based on the selection
filtered_df = df[
    ((df["Country"] == country) | (country == "All")) &
    ((df["Industry"] == industry) | (industry == "All")) &
    ((df["Year"] == year) | (year == "All"))
]

# Mostrar tabla de datos
st.subheader("Datos filtrados")
st.dataframe(filtered_df.style.format({"Value_M_USD": "${:,.2f}", "Growth_Percentage": "{:.2f}%"}),
             hide_index=True)

# Visualizaciones
st.subheader("Visualizaciones")

# Gráfico de barras de ventas por industria
sales_by_industry = filtered_df.groupby("Industry")["Value_M_USD"].sum().sort_values()
st.bar_chart(sales_by_industry)

# Gráfico de líneas de crecimiento por año
growth_by_year = filtered_df.groupby("Year")["Growth_Percentage"].mean()
st.line_chart(growth_by_year)
col1, col2 = st.columns([3, 3]) 
with col1:
    st.subheader("Resumen de ventas")
    summary = filtered_df.groupby(["Country", "Industry"])["Value_M_USD"].sum().reset_index()
    #st.write(summary.style.format({"Value_M_USD": "${:,.2f}"}))
    st.dataframe(summary.style.format({"Value_M_USD": "${:,.2f}"}), hide_index=True)

# Mostrar métricas generales
with col2:
    total_sales = filtered_df["Value_M_USD"].sum()
    average_growth = filtered_df["Growth_Percentage"].mean()
    st.metric("Ventas totales (USD)", f"${total_sales:,.2f}")
    st.metric("Crecimiento promedio (%)", f"{average_growth:.2f}%")