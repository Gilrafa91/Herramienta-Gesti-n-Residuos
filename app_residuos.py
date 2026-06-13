import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import sqlite3

st.set_page_config(page_title="Gestión de Reciclaje - Rafael Gil", layout="wide")

st.title("♻️ Gestión de Reciclaje")
st.subheader("Rafael Gil Terán - Ingeniero en Recursos Naturales")

# Base de datos
conn = sqlite3.connect('residuos.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS residuos (
    id INTEGER PRIMARY KEY, fecha TEXT, tipo TEXT, cantidad REAL, unidad TEXT,
    origen TEXT, valorizacion TEXT, valor_ganancia REAL, notas TEXT
)''')
conn.commit()

# Registro
with st.expander("📝 Registrar Nueva Entrada", expanded=True):
    with st.form("registro"):
        col1, col2 = st.columns(2)
        fecha = col1.date_input("Fecha", datetime.today())
        tipo = col2.selectbox("Tipo de Material", ["Papel", "Cartón", "Plástico", "Vidrio", "Orgánico", "Madera", "Latas", "Metales", "Peligroso", "Residuo No Valorizable", "Otros"])
        
        col3, col4 = st.columns(2)
        cantidad = col3.number_input("Cantidad", min_value=0.0, value=1000.0)
        unidad = col4.selectbox("Unidad", ["ton", "kg"])
        
        origen = st.text_input("Origen / Cliente", "Ej: Empresa XYZ")
        valorizacion = st.selectbox("Valorización", ["Reciclaje", "Compost", "Disposición Final", "Otro"])
        notas = st.text_area("Notas")
        
        if st.form_submit_button("💾 Guardar Registro", type="primary"):
            ganancia_por_ton = {"Papel":130,"Cartón":85,"Plástico":260,"Vidrio":65,"Orgánico":45,
                               "Madera":75,"Latas":320,"Metales":380,"Peligroso":-150,
                               "Residuo No Valorizable":0,"Otros":40}
            factor = 1 if unidad == "ton" else 0.001
            ganancia = round(cantidad * ganancia_por_ton.get(tipo, 50) * factor * 950, 2)  # Por defecto CLP
            
            c.execute("INSERT INTO residuos VALUES (NULL,?,?,?,?,?,?,?,?)", 
                      (str(fecha), tipo, cantidad, unidad, origen, valorizacion, ganancia, notas))
            conn.commit()
            st.success("✅ Registro guardado!")

# Mostrar registros
st.header("📋 Registros")
df = pd.read_sql_query("SELECT * FROM residuos ORDER BY fecha DESC", conn)

if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    total = df['cantidad'].sum()
    valor_total = df['valor_ganancia'].sum()
    st.metric("Total Gestionado", f"{total:,.1f} ton")
    st.metric("Valor Estimado", f"${valor_total:,.2f}")
else:
    st.info("Aún no hay registros")

# Certificado simple
st.header("🎖️ Certificado")
if not df.empty:
    idx = st.selectbox("Seleccionar registro", df.index, format_func=lambda x: f"{df.loc[x,'fecha']} - {df.loc[x,'tipo']}")
    if st.button("Generar Certificado PDF"):
        row = df.loc[idx]
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "CERTIFICADO DE RECICLAJE", ln=1, align='C')
        pdf.cell(0, 10, f"Fecha: {row['fecha']}", ln=1)
        pdf.cell(0, 10, f"Material: {row['tipo']}", ln=1)
        pdf.cell(0, 10, f"Cantidad: {row['cantidad']} {row['unidad']}", ln=1)
        pdf.cell(0, 10, f"Cliente: {row['origen']}", ln=1)
        pdf.cell(0, 10, f"Valor: ${row['valor_ganancia']:,.2f}", ln=1)
        pdf.output("certificado.pdf")
        
        with open("certificado.pdf", "rb") as f:
            st.download_button("⬇️ Descargar Certificado", f, file_name="Certificado_Reciclaje.pdf")

st.caption("Versión Ultra Simple - Rafael Gil Terán")