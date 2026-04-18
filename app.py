import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from engine import generate_forecast
from alert_system import calculate_alerts

st.set_page_config(page_title="StockGuard | Industrial Stock Analytics", page_icon="📈", layout="wide")

st.markdown("""\n<style>\n    .kpi-card {\n        background-color: rgba(123, 97, 255, 0.1);\n        border: 1px solid rgba(123, 97, 255, 0.3);\n        border-radius: 10px;\n        padding: 20px;\n        text-align: center;\n    }\n    .kpi-val { font-size: 2rem; font-weight: 700; color: white; }\n    .kpi-label { font-size: 0.9rem; color: #A5A1C0; text-transform: uppercase; }\n</style>\n""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    import os
    file_path = "data/synthetic_industrial_machine_data.csv"
    if not os.path.exists(file_path):
        st.info("Generating synthetic data for StockGuard...")
        from data_mock import generate_synthetic_data
        os.makedirs("data", exist_ok=True)
        generate_synthetic_data(file_path)
        st.success("Data generated successfully!")
    df = pd.read_csv(file_path)
    df['Posting_Date'] = pd.to_datetime(df['Posting_Date'])
    return df



df = load_data()
if df.empty:
    st.stop()
    
# --- MULTI-FACILITY DASHBOARD ---

st.sidebar.header("Global Analytics Filter")
plants = df['Plant_Code'].unique().tolist()
selected_plant = st.sidebar.selectbox("Select Research Facility", plants)

plant_df = df[df['Plant_Code'] == selected_plant]
materials = plant_df['Material_Name'].unique().tolist()

selected_mat_name = st.sidebar.selectbox("Isolate Specific Component", materials)

# Extract specific material
mat_df = plant_df[plant_df['Material_Name'] == selected_mat_name].copy()
mat_df = mat_df.sort_values('Posting_Date')

# Component Snapshot
latest_record = mat_df.iloc[-1]
mat_id = latest_record['Material_ID']
c_stock = float(latest_record['Current_Stock'])
s_stock = float(latest_record['Safety_Stock'])
l_time = int(latest_record['Lead_Time_Days'])
desc = latest_record['Material_Description']

st.sidebar.markdown(f"**Component ID:** {mat_id}")
st.sidebar.markdown(f"**Info:** {desc}")
st.sidebar.markdown(f"**Vendor Lead Time:** {l_time} days")
st.sidebar.markdown(f"**Safety Stock Barrier:** {s_stock}")

# --- AI FORECASTING EXECUTION ---
with st.spinner(f"Running Prophet/MA Prediction Engine on {mat_id}..."):
    forecast_df = generate_forecast(df, mat_id, forecast_days=30)
alerts = calculate_alerts(forecast_df, c_stock, s_stock, l_time)

# --- KPIS ---
col1, col2, col3 = st.columns(3)
with col1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Live Physical Stock</div><div class='kpi-val'>{c_stock:.0f}</div></div>", unsafe_allow_html=True)
with col2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Days To Safety Breach</div><div class='kpi-val'>{alerts['days_until_safety_stock']}</div></div>", unsafe_allow_html=True)
with col3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>ERP Status</div><div class='kpi-val' style='color:#ffaa00;'>{alerts['status']}</div></div>", unsafe_allow_html=True)

st.divider()

# --- ADVANCED UI GRAPHS (Requested Components) ---

colA, colB = st.columns(2)

with colA:
    st.subheader("🏭 Facility Inventory Distribution")
    # Generate aggregate for bar chart: Latest mock stock for each material in the plant (limit top 15 for visibility)
    snapshot = plant_df.drop_duplicates(subset=['Material_Name'], keep='last').sort_values(by='Current_Stock', ascending=False).head(15)
    bar_data = snapshot.set_index('Material_Name')[['Current_Stock', 'Safety_Stock']]
    fig = px.bar(bar_data, title="Facility Inventory Distribution")
    st.plotly_chart(fig)
    st.caption("Plotly bar chart: Shows the Current Stock and Safety Stock baselines for the highest-volume components.")

with colB:
    st.subheader("⚠️ Supply Chain Risk Matrix")
    # Scatter chart: Lead Time vs Safety Stock
    scatter_data = plant_df.drop_duplicates(subset=['Material_Name'], keep='last')
    fig_scatter = px.scatter(scatter_data, x='Lead_Time_Days', y='Safety_Stock', size='Current_Stock', color='Current_Stock')
    st.plotly_chart(fig_scatter)
    st.caption("Plotly scatter: Plots Vendor Lead Time against Safety Stock thresholds. Larger bubbles = higher stock.")

st.divider()

colC, colD = st.columns(2)

with colC:
    st.subheader(f"📊 {selected_mat_name} Depletion Surface")
    # Area Chart: cumulative sum of consumed material over the last 90 days
    last_90 = mat_df.tail(90).copy()
    last_90['Cumulative_Consumption'] = last_90['Quantity_Consumed'].cumsum()
    fig_area = px.area(last_90.set_index('Posting_Date')['Cumulative_Consumption'], title=f"{selected_mat_name} Depletion")
    st.plotly_chart(fig_area, color_discrete_sequence=['#7B61FF'])
    st.caption("Plotly area chart: Visualizes cumulative usage over past 90 days.")

with colD:
    st.subheader("🔮 Prophet Predictive Timeline")
    # Just standard Line Chart comparing historical to actual
    last_30_hist = last_90.tail(30)[['Posting_Date', 'Quantity_Consumed']].rename(columns={'Posting_Date': 'ds', 'Quantity_Consumed': 'y'})
    fut_30 = forecast_df[['ds', 'yhat']].rename(columns={'yhat': 'y'})
    line_df = pd.concat([last_30_hist, fut_30])
    fig_line = px.line(line_df, x='ds', y='y', title="Historical vs Forecast")
    st.plotly_chart(fig_line)
    st.caption("Plotly line chart: Historical usage vs AI forecast.")

st.divider()

# --- AUTOMATED SAP PR GENERATION ---
st.subheader("SAP Material Management Actions")
st.write(f"Based on the intelligent forecasting, `{selected_mat_name}` has a status of: **{alerts['status']}**.")
from fpdf import FPDF

def generate_pdf_report(plant, mat_id, mat_name, qty, deliv_date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="SAP PURCHASE REQUISITION (PR)", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Facility Code: {plant}", ln=True)
    pdf.cell(200, 10, txt=f"Material ID: {mat_id}", ln=True)
    pdf.cell(200, 10, txt=f"Material Name: {mat_name}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Authorized Reorder Quantity: {'{:.0f}'.format(qty)}", ln=True)
    pdf.cell(200, 10, txt=f"Required Delivery Date: {deliv_date}", ln=True)
    
    filename = f"PR_Output_{mat_id}.pdf"
    pdf.output(filename)
    with open(filename, "rb") as f:
        bytes_data = f.read()
    try:
        os.remove(filename)
    except:
        pass
    return bytes_data

if st.button("Simulate BAPI PR Generation via RFC"):
    pr_qty = float(s_stock * 2)
    pr_date = str(alerts['reorder_trigger_date'])
    
    st.success(f"Action Executed: Sent Purchase Requisition payload for Component {mat_id} to internal PR queue.")
    st.json({
        "BAPI_PR_CREATE1": {
            "PLANT": selected_plant,
            "MATERIAL": mat_id,
            "QUANTITY": pr_qty,
            "DELIV_DATE": pr_date
        }
    })
    
    # Render PDF Download Button
    pdf_bytes = generate_pdf_report(selected_plant, mat_id, selected_mat_name, pr_qty, pr_date)
    st.download_button(
        label="📄 Download Official PR Document (PDF)",
        data=pdf_bytes,
        file_name=f"SAP_PR_{mat_id}.pdf",
        mime="application/pdf"
    )
