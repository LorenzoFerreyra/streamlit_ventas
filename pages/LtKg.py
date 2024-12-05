import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px
from Ventas import convert_df
import login as login

st.set_page_config(page_title="Tablero de análisis por Lt/Kg", layout="centered")

login.generarLogin()
if 'usuario' in st.session_state:
    path = Path("data/datos.xlsx")

    df = pd.read_excel(path, sheet_name="LtKg", header=None)

    login.generarLogin()
    if 'usuario' in st.session_state:
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
        df = melted_df.drop(columns=["Country_Metric"])

        st.title("Análisis de métricas Lt/Kg")

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
        st.dataframe(filtered_df,  hide_index=True)
        csv = convert_df(filtered_df)
        st.download_button(
            label="Descarga tus datos filtrados como CSV",
            data=csv,
            file_name="large_df.csv",
            mime="text/csv",
        )

        # Visualizaciones interactivas con Plotly
        st.header("Visualizaciones Interactivas")

        # 1. Gráfico de barras: Comparación por país
        st.subheader("Distribución por País")
        bar_chart = px.bar(
            filtered_df,
            x="Country",
            y="Value",
            color="Metric",
            barmode="group",
            title="Distribución de Métricas por País",
            labels={"Value": "Valor", "Country": "País", "Metric": "Métrica"}
        )
        st.plotly_chart(bar_chart)

        # 2. Gráfico de barras apiladas: Distribución por año y sector
        st.subheader("Distribución por Año y Sector")
        stacked_bar_chart = px.bar(
            filtered_df,
            x="Year",
            y="Value",
            color="Sector",
            barmode="stack",
            title="Distribución de Valores por Año y Sector",
            labels={"Value": "Valor", "Year": "Año", "Sector": "Sector"}
        )
        st.plotly_chart(stacked_bar_chart)

        # 3. Gráfico de área: Tendencias por sector
        st.subheader("Tendencias por Sector")
        area_chart = px.area(
            filtered_df,
            x="Year",
            y="Value",
            color="Sector",
            title="Tendencias por Sector",
            labels={"Value": "Valor", "Year": "Año", "Sector": "Sector"}
        )
        st.plotly_chart(area_chart)

        # 4. Gráfico de barras horizontal: Total por Métrica y País
        st.subheader("Total por Métrica y País")
        horizontal_bar_chart = px.bar(
            filtered_df,
            x="Value",
            y="Country",
            color="Metric",
            orientation="h",
            title="Total por Métrica y País",
            labels={"Value": "Valor", "Country": "País", "Metric": "Métrica"}
        )
        st.plotly_chart(horizontal_bar_chart)
        btnSalir=st.button("Cerrar sesión",key='ltkg')
        if btnSalir:
            st.session_state.clear()
            st.rerun()