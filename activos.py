import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Cargar datos por el usuario
st.set_page_config("Dashboard de Pagos", layout="wide")
st.title("📊 Dashboard de Pagos")

archivo = st.file_uploader("📂 Sube tu archivo Excel de pagos", type=["xlsx"])
if archivo:
    df = pd.read_excel(archivo, sheet_name=0)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
    df.dropna(subset=["Fecha"], inplace=True)
    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.month

    # Filtros
    nombres = df["Nombre"].unique()
    años = sorted(df["Año"].dropna().unique())

    col1, col2 = st.columns(2)
    with col1:
        filtro_nombre = st.multiselect("Filtrar por nombre:", options=nombres, default=nombres)
    with col2:
        filtro_año = st.multiselect("Filtrar por año:", options=años, default=años)

    # Aplicar filtros
    df_filtrado = df[(df["Nombre"].isin(filtro_nombre)) & (df["Año"].isin(filtro_año))]

    # KPIs
    monto_total = df_filtrado["Monto"].sum()
    pagos_totales = df_filtrado.shape[0]
    monto_por_persona = df_filtrado.groupby("Nombre")["Monto"].sum()
    persona_max_pago = monto_por_persona.idxmax()
    monto_max = monto_por_persona.max()
    monto_anual = df_filtrado.groupby("Año")["Monto"].sum()
    prom_mensual = df_filtrado.groupby(["Año", "Mes"])["Monto"].sum().mean()

    # Mostrar KPIs
    st.subheader("🔢 Indicadores Clave")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Monto total pagado", f"${monto_total:,.2f}")
    kpi2.metric("Total de pagos registrados", pagos_totales)
    kpi3.metric("Promedio mensual de pagos", f"${prom_mensual:,.2f}")

    kpi4, kpi5, kpi6 = st.columns(3)
    kpi4.metric("Persona que más ha pagado", persona_max_pago)
    kpi5.metric("Monto total de esa persona", f"${monto_max:,.2f}")
    kpi6.metric("Años registrados", f"{', '.join(map(str, filtro_año))}")

    # Gráfico de pagos por persona
    st.subheader("💰 Pagos por Persona")
    fig1 = px.bar(monto_por_persona.sort_values(), orientation='h', labels={"value": "Monto Total", "index": "Nombre"})
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico de pagos por año
    st.subheader("📆 Pagos por Año")
    fig2 = px.bar(monto_anual, labels={"value": "Monto Total", "Año": "Año"})
    st.plotly_chart(fig2, use_container_width=True)

    # Línea temporal de pagos
    st.subheader("📈 Línea Temporal de Pagos")
    df_temporal = df_filtrado.groupby("Fecha")["Monto"].sum().reset_index()
    fig3 = px.line(df_temporal, x="Fecha", y="Monto", labels={"Monto": "Monto Diario"})
    st.plotly_chart(fig3, use_container_width=True)

    # Tabla detallada
    st.subheader("📋 Tabla Detallada de Pagos Filtrados")
    df_ordenado = df_filtrado.sort_values("Fecha")
    st.dataframe(df_ordenado, use_container_width=True)

    # Botón de descarga
    st.download_button(
        label="📥 Descargar datos filtrados en Excel",
        data=BytesIO(df_ordenado.to_excel(index=False, engine='xlsxwriter')),
        file_name="pagos_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.caption("Desarrollado por ChatGPT para análisis de pagos.")
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")

