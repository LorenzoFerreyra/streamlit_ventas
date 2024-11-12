import pandas as pd
import numpy as np
import streamlit as st

path = '/home/lorenzo/Documents/Freelance/Streamlit Mexico/BasedatosproyectoVisualizacin.xlsx'
all_sheets = pd.read_excel(path, sheet_name=None, skiprows=2)

sheets_to_exclude = ["LtKG", "Empaque", "Marcas"]

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

st.write(df)

# Configurar título y descripción del tablero
st.title("Tablero de Análisis de Ventas")
st.markdown("Este tablero muestra los datos de ventas por industria, sector y categoría, y permite aplicar filtros interactivos.")

# Configurar filtros
st.sidebar.header("Filtros")
countries = st.sidebar.multiselect("País", options=df["Country"].unique(), default=df["Country"].unique())
industries = st.sidebar.multiselect("Industria", options=df["Industry"].unique(), default=df["Industry"].unique())
years = st.sidebar.slider("Año", int(df["Year"].min()), int(df["Year"].max()), (int(df["Year"].min()), int(df["Year"].max())))

# Aplicar filtros
filtered_df = df[(df["Country"].isin(countries)) & 
                 (df["Industry"].isin(industries)) & 
                 (df["Year"].between(years[0], years[1]))]

# Mostrar tabla de datos
st.subheader("Datos filtrados")
st.dataframe(filtered_df.style.format({"Value_M_USD": "${:,.2f}", "Growth_Percentage": "{:.2f}%"}))

# Visualizaciones
st.subheader("Visualizaciones")

# Gráfico de barras de ventas por industria
sales_by_industry = filtered_df.groupby("Industry")["Value_M_USD"].sum().sort_values()
st.bar_chart(sales_by_industry)

# Gráfico de líneas de crecimiento por año
growth_by_year = filtered_df.groupby("Year")["Growth_Percentage"].mean()
st.line_chart(growth_by_year)

# Tabla resumida
st.subheader("Resumen de Ventas")
summary = filtered_df.groupby(["Country", "Industry"])["Value_M_USD"].sum().reset_index()
st.write(summary.style.format({"Value_M_USD": "${:,.2f}"}))

# Mostrar métricas generales
total_sales = filtered_df["Value_M_USD"].sum()
average_growth = filtered_df["Growth_Percentage"].mean()
st.metric("Ventas Totales (USD)", f"${total_sales:,.2f}")
st.metric("Crecimiento Promedio (%)", f"{average_growth:.2f}%")