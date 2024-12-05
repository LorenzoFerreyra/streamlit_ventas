import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
import folium
from streamlit_folium import st_folium
import login as login




# Configuración inicial de la página
st.set_page_config(page_title="Tablero de análisis de ventas globales", layout="wide")


def convert_df(df):
    return df.to_csv().encode("utf-8")




def load_data():
    path = Path("data/datos.xlsx")
    all_sheets = pd.read_excel(path, sheet_name=None, skiprows=2)
    sheets_to_exclude = ["LtKg", "Empaque", "Marcas"]
    df_list = []

    for sheet_name, df in all_sheets.items():
        if sheet_name in sheets_to_exclude:
            continue
        
        if df.shape[1] >= 6:
            df = df.iloc[:, :6]
            df.columns = ['Industry', 'Sector', 'Category', 'Year', 'Value_M_USD', 'Growth_Percentage']
        else:
            print(f"Advertencia: La hoja {sheet_name} no tiene suficientes columnas.")
            continue
        
        df[['Industry', 'Sector', 'Category']] = df[['Industry', 'Sector', 'Category']].ffill()
        df['Value_M_USD'] = df['Value_M_USD'].replace({',': '', '-': np.nan}, regex=True).astype(float)
        df['Growth_Percentage'] = df['Growth_Percentage'].astype(str).str.replace('%', '').replace('-', np.nan).astype(float)
        df['Country'] = sheet_name
        df_list.append(df)

    return pd.concat(df_list, ignore_index=True)

def display_map(df, selected_countries):

    
    # Crear el mapa base
    map = folium.Map(location=[20, 0], zoom_start=2, scrollWheelZoom=False, tiles='CartoDB positron')
    
    # Preparar datos para el mapa
    country_data = df.groupby('Country')['Value_M_USD'].sum().reset_index()
    
    # Cargar el GeoJSON de países desde URL
    geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
    
    # Crear el choropleth
    choropleth = folium.Choropleth(
        geo_data=geojson_url,
        data=country_data,
        columns=('Country', 'Value_M_USD'),
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        highlight=True
    )
    choropleth.geojson.add_to(map)

    # Crear un diccionario de valores por país para el tooltip
    country_dict = dict(zip(country_data.Country, country_data.Value_M_USD))

    # Agregar tooltips personalizados
    for feature in choropleth.geojson.data['features']:
        country_name = feature['properties']['name']
        if country_name in country_dict:
            value = country_dict[country_name]
            feature['properties']['value'] = f"${value:,.2f}M USD"
        else:
            feature['properties']['value'] = 'No data'

    # Agregar tooltips mejorados
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=['name', 'value'],
            aliases=['País:', 'Ventas:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )
    
    st_map = st_folium(map, width=None, height=400)
    
    # Obtener el país seleccionado
    selected_country = None
    if st_map['last_active_drawing']:
        selected_country = st_map['last_active_drawing']['properties']['name']
    
    return selected_country

def main():
    st.title("Tablero de análisis de ventas")
    st.markdown("Este tablero muestra los datos de ventas por industria, sector y categoría, y permite aplicar filtros interactivos.")

    # Cargar datos
    df = load_data()

    # Contenedor para filtros
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
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Mapa de Ventas por País")
        selected_country = display_map(filtered_df, countries)
        if selected_country:
            st.info(f"País seleccionado: {selected_country}")

    with col2:
        st.subheader("Métricas Generales")
        total_sales = filtered_df["Value_M_USD"].sum()
        average_growth = filtered_df["Growth_Percentage"].mean()
        st.metric("Ventas totales (USD)", f"${total_sales:,.2f}")
        st.metric("Crecimiento promedio (%)", f"{average_growth:.2f}%")

    # Datos y visualizaciones
    st.subheader("Datos filtrados")
    st.dataframe(
        filtered_df.style.format({"Value_M_USD": "${:,.2f}", "Growth_Percentage": "{:.2f}%"}),
        hide_index=True
    )
    csv = convert_df(filtered_df)

    st.download_button(
        label="Descarga tus datos filtrados como CSV",
        data=csv,
        file_name="large_df.csv",
        mime="text/csv",
    )

    # Visualizaciones
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Ventas por Industria")
        sales_by_industry = filtered_df.groupby("Industry")["Value_M_USD"].sum().sort_values()
        st.bar_chart(sales_by_industry)

    with col4:
        st.subheader("Crecimiento por Año")
        growth_by_year = filtered_df.groupby("Year")["Growth_Percentage"].mean()
        st.line_chart(growth_by_year)

    # Resumen de ventas
    st.subheader("Resumen de ventas por País e Industria")
    summary = filtered_df.groupby(["Country", "Industry"])["Value_M_USD"].sum().reset_index()
    st.dataframe(summary.style.format({"Value_M_USD": "${:,.2f}"}), hide_index=True,
                 use_container_width=True)

login.generarLogin()
if 'usuario' in st.session_state:
    st.subheader('Bienvenidos')
    if __name__ == "__main__":
        main()
        btnSalir=st.button("Cerrar sesión",key='ventas')
        if btnSalir:
            st.session_state.clear()
            # Luego de borrar el Session State reiniciamos la app para mostrar la opción de usuario y clave
            st.rerun()
