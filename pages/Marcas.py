import pandas as pd
import streamlit as st
from pathlib import Path
from Ventas import convert_df
import plotly.express as px
import login as login

# Configuración de la página
st.set_page_config(page_title="Tablero de análisis de marca", layout="centered")


login.generarLogin()
if 'usuario' in st.session_state:

    def load_data():
        path = Path("data/datos.xlsx")
        df = pd.read_excel(path, sheet_name="Marcas", header=None)

        # Extraer las primeras tres filas para el encabezado
        header_rows = df.iloc[:3]
        header_rows = header_rows.fillna(method="ffill", axis=1)
        columns = header_rows.apply(lambda x: "_".join(x.dropna().astype(str)), axis=0)

        df = df.iloc[3:]
        df.columns = columns

        return df

    # Cargar los datos con el cache aplicado
    df = load_data()



    def process_data(df):
        melted_df = df.melt(
            id_vars=['Year','Sector','Segment','Category','Trademark Owner','Brand'],
            var_name="Country_Metric",
            value_name="Value",
        )
        melted_df[["Country", "Metric"]] = melted_df["Country_Metric"].str.rsplit("_", n=1, expand=True)
        melted_df[['Year','Sector','Segment','Category','Trademark Owner','Brand']] = melted_df[['Year','Sector','Segment','Category','Trademark Owner','Brand']].fillna(method='ffill')
        df = melted_df.drop(columns=["Country_Metric"])
        df["Value"] = df["Value"].replace("-", 0).astype(float)
        return df

    # Procesar los datos con el cache aplicado
    df = process_data(df)

    # Mostrar el título y la tabla de datos
    st.title("Análisis de performance de marcas")
    st.dataframe(df, hide_index=True)

    # Filtros en la barra lateral
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

    def apply_filters(df, countries, sectors, segments, categories, trademark_owners, brands, years):
        filtered_df = df[
            (df["Country"].isin(countries) | ("All" in countries)) &
            (df["Sector"].isin(sectors) | ("All" in sectors)) &
            (df["Segment"].isin(segments) | ("All" in segments)) &
            (df["Category"].isin(categories) | ("All" in categories)) &
            (df["Trademark Owner"].isin(trademark_owners) | ("All" in trademark_owners)) &
            (df["Brand"].isin(brands) | ("All" in brands)) &
            (df["Year"].astype(str).isin(years) | ("All" in years))
        ]
        return filtered_df

    # Aplicar los filtros con cache
    filtered_df = apply_filters(df, countries, sectors, segments, categories, trademark_owners, brands, years)

    # Generar archivo CSV para descarga
    csv = convert_df(filtered_df)

    st.download_button(
        label="Descarga tus datos como CSV",
        data=csv,
        file_name="large_df.csv",
        mime="text/csv",
    )

    # Calcular las métricas
    total_unidades = filtered_df["Value"].count()
    ventas_totales = filtered_df["Value"].sum()

    # Mostrar las métricas
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Unidades Vendidas", f"{total_unidades:,}")
    with col2:
        st.metric("Ventas Totales", f"${ventas_totales:,.2f}")

    # Graficar los gráficos

    def plot_stacked_bar_sector_segment(filtered_df):
        stacked_bar_sector_segment = px.bar(
            filtered_df.groupby(['Sector', 'Segment'])['Value'].sum().reset_index(),
            x="Sector",
            y="Value",
            color="Segment",
            title="Distribución de Ventas por Sector y Segmento",
            labels={"Value": "Ventas", "Sector": "Sector", "Segment": "Segmento"}
        )
        return stacked_bar_sector_segment

    # Mostrar gráfico de barras apiladas
    st.plotly_chart(plot_stacked_bar_sector_segment(filtered_df))


    def plot_bar_owner_brand(filtered_df):
        bar_owner_brand = px.bar(
            filtered_df.groupby(['Trademark Owner', 'Brand'])['Value'].sum().reset_index(),
            x="Trademark Owner",
            y="Value",
            color="Brand",
            title="Ventas por Propietario de Marca y Marca",
            labels={"Value": "Ventas", "Trademark Owner": "Propietario de Marca", "Brand": "Marca"}
        )
        return bar_owner_brand

    # Mostrar gráfico de barras por Propietario y Marca
    st.plotly_chart(plot_bar_owner_brand(filtered_df))


    def plot_histogram_segment(filtered_df):
        histogram_segment = px.histogram(
            filtered_df,
            x="Value",
            color="Segment",
            nbins=30,
            title="Distribución de Ventas por Segmento",
            labels={"Value": "Ventas", "Segment": "Segmento"}
        )
        return histogram_segment

    # Mostrar histograma de ventas por Segmento
    st.plotly_chart(plot_histogram_segment(filtered_df))
    btnSalir=st.button("Cerrar sesión",key='marcas')
    if btnSalir:
        st.session_state.clear()
        st.rerun()

