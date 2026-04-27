import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# Set page configuration FIRST
st.set_page_config(page_title="CRM Sales Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS Injection: Cyberpunk + ColorHunt Palette ---
# Deep Dark Grey: #222831
# Medium Grey: #393E46
# Vibrant Cyan: #00ADB5
# Off White: #EEEEEE
st.markdown("""
<style>
    div.block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #111418, #222831, #2d3540, #1b2027);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    [data-testid="stSidebar"] {
        background: rgba(34, 40, 49, 0.7) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-right: 1px solid rgba(0, 173, 181, 0.3);
    }
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, label, .css-10trblm {
        color: #EEEEEE !important;
        text-shadow: 0px 0px 5px rgba(238, 238, 238, 0.3);
    }
    .kpi-card {
        border-radius: 12px;
        padding: 10px 15px;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(57, 62, 70, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(238, 238, 238, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 15px rgba(0, 173, 181, 0.4);
    }
    .kpi-card h2 { 
        margin: 0; 
        font-size: 2rem; 
        color: #00ADB5 !important; 
        text-shadow: 0 0 10px rgba(0, 173, 181, 0.6);
    }
    .kpi-card p { 
        margin: 0; 
        font-size: 0.85rem; 
        font-weight: bold; 
        color: #EEEEEE;
        opacity: 0.9;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .kpi-red { border-left: 3px solid #00ADB5; box-shadow: 0 0 10px rgba(0, 173, 181, 0.2); }
    .kpi-blue { border-left: 3px solid #EEEEEE; box-shadow: 0 0 10px rgba(238, 238, 238, 0.2); }
    .kpi-green { border-left: 3px solid #00ADB5; box-shadow: 0 0 10px rgba(0, 173, 181, 0.2); }
    .sidebar-title {
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
        margin-top: -30px;
        color: #00ADB5;
        text-shadow: 0 0 8px #00ADB5;
        letter-spacing: 2px;
    }
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Time to load up the data! We'll grab the files from the parent directory
# and join the fact table (sales_pipeline) to our dimension tables.
@st.cache_data
def load_and_merge_data():
    base_path = '../' # Parent directory where CSVs are located
    
    # Read tables
    try:
        sales_pipeline = pd.read_csv(os.path.join(base_path, 'sales_pipeline.csv'))
        sales_teams = pd.read_csv(os.path.join(base_path, 'sales_teams.csv'))
        products = pd.read_csv(os.path.join(base_path, 'products.csv'))
        accounts = pd.read_csv(os.path.join(base_path, 'accounts.csv'))
    except FileNotFoundError:
        st.error("Could not find the CSV files in the parent directory.")
        return pd.DataFrame()

    # Join tables
    df = pd.merge(sales_pipeline, sales_teams, on='sales_agent', how='left')
    df = pd.merge(df, products, on='product', how='left')
    df = pd.merge(df, accounts, on='account', how='left')
    
    # Clean & format dates
    df['engage_date'] = pd.to_datetime(df['engage_date'], errors='coerce')
    df['close_date'] = pd.to_datetime(df['close_date'], errors='coerce')
    
    # Calculate Sales Cycle Length (in days)
    df['sales_cycle_duration'] = (df['close_date'] - df['engage_date']).dt.days
    
    # Ensure numeric columns
    df['close_value'] = pd.to_numeric(df['close_value'], errors='coerce')
    
    return df

df = load_and_merge_data()

if df.empty:
    st.stop()

# Hooking up the sidebar filters. 
# We're letting the user slice the data by Region and Manager.
st.sidebar.markdown('<div class="sidebar-title">CRM NEXUS</div>', unsafe_allow_html=True)

st.sidebar.markdown("<br><p style='font-size:0.85rem; margin-bottom: 0px;'>FILTERS</p>", unsafe_allow_html=True)
selected_region = st.sidebar.selectbox("Regional Office", ["All"] + list(df['regional_office'].dropna().unique()))
selected_manager = st.sidebar.selectbox("Manager", ["All"] + list(df['manager'].dropna().unique()))

# Apply filters
filtered_df = df.copy()
if selected_region != "All":
    filtered_df = filtered_df[filtered_df['regional_office'] == selected_region]
if selected_manager != "All":
    filtered_df = filtered_df[filtered_df['manager'] == selected_manager]

# The KPI Engine: Let's crunch the numbers for the top row summary cards.
# We have to be careful to only calculate revenue for 'Won' deals!
won_deals = filtered_df[filtered_df['deal_stage'] == 'Won']
lost_deals = filtered_df[filtered_df['deal_stage'] == 'Lost']

# 1. Total Pipeline Revenue (Won deals)
total_revenue = won_deals['close_value'].sum()

# 2. Overall Win Rate
total_closed = len(won_deals) + len(lost_deals)
win_rate = (len(won_deals) / total_closed * 100) if total_closed > 0 else 0

# 3. Average Deal Size (Won deals)
avg_deal_size = won_deals['close_value'].mean()
if pd.isna(avg_deal_size): avg_deal_size = 0

# 4. Average Sales Cycle (Won deals)
avg_sales_cycle = won_deals['sales_cycle_duration'].mean()
if pd.isna(avg_sales_cycle): avg_sales_cycle = 0

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <div>
            <h2>${total_revenue:,.0f}</h2>
            <p>Total Revenue</p>
        </div>
        <div style="font-size: 2.5rem; text-shadow: 0 0 10px #00ADB5;">💎</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div>
            <h2 style="color: #EEEEEE !important;">{win_rate:.1f}%</h2>
            <p>Win Rate</p>
        </div>
        <div style="font-size: 2.5rem; text-shadow: 0 0 10px rgba(238,238,238,0.5);">🎯</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card kpi-red">
        <div>
            <h2>${avg_deal_size:,.0f}</h2>
            <p>Avg Deal Size</p>
        </div>
        <div style="font-size: 2.5rem; text-shadow: 0 0 10px #00ADB5;">📈</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div>
            <h2 style="color: #EEEEEE !important;">{avg_sales_cycle:.1f} d</h2>
            <p>Avg Sales Cycle</p>
        </div>
        <div style="font-size: 2.5rem; text-shadow: 0 0 10px rgba(238,238,238,0.5);">⏱️</div>
    </div>
    """, unsafe_allow_html=True)

# Quick config to make sure our Plotly charts perfectly match the sleek 
# Cyberpunk aesthetic we injected via CSS earlier.
layout_config = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#EEEEEE', size=10, family="Courier New, monospace"),
    margin=dict(l=10, r=10, t=30, b=10)
)
grid_config = dict(showgrid=True, gridwidth=1, gridcolor='rgba(0, 173, 181, 0.1)', zeroline=False)
color_sequence = ['#00ADB5', '#EEEEEE', '#393E46']

# Let's paint the charts! 
# We're using a 2-row grid to keep everything visible without scrolling.

row1_col1, row1_col2 = st.columns([1.5, 1])

with row1_col1:
    # Bar Chart: Revenue by Regional Office & Manager
    rev_by_region = won_deals.groupby(['regional_office', 'manager'], as_index=False)['close_value'].sum()
    fig1 = px.bar(rev_by_region, x='regional_office', y='close_value', color='manager',
                  title="REVENUE BY REGION & MANAGER", height=240, barmode='group',
                  color_discrete_sequence=['#00ADB5', '#EEEEEE', '#393E46', '#222831'])
    fig1.update_layout(**layout_config, legend_title_text=None)
    fig1.update_xaxes(**grid_config, title=None)
    fig1.update_yaxes(**grid_config, title=None)
    st.plotly_chart(fig1, width='stretch')

with row1_col2:
    # Funnel Chart: Deal Stage Drop-off
    stage_counts = filtered_df['deal_stage'].value_counts().reindex(['Prospecting', 'Engaging', 'Won', 'Lost']).reset_index()
    stage_counts.columns = ['deal_stage', 'count']
    fig2 = px.funnel(stage_counts, x='count', y='deal_stage', 
                     title="SALES FUNNEL", height=240,
                     color_discrete_sequence=['#00ADB5'])
    fig2.update_layout(**layout_config)
    st.plotly_chart(fig2, width='stretch')

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    # Scatter Plot: Cycle Length vs Close Value
    fig3 = px.scatter(won_deals, x='sales_cycle_duration', y='close_value', 
                      title="CYCLE DURATION VS VALUE", height=240,
                      color_discrete_sequence=['#00ADB5'])
    fig3.update_traces(marker=dict(size=6, opacity=0.7, line=dict(width=1, color='#EEEEEE')))
    fig3.update_layout(**layout_config)
    fig3.update_xaxes(**grid_config, title="Days")
    fig3.update_yaxes(**grid_config, title="$")
    st.plotly_chart(fig3, width='stretch')

with row2_col2:
    # Horizontal Bar: Win Rates by Sector
    sector_won = won_deals.groupby('sector').size()
    sector_total = filtered_df[filtered_df['deal_stage'].isin(['Won', 'Lost'])].groupby('sector').size()
    
    # Avoid division by zero by filling NaNs
    win_rate_sector = (sector_won / sector_total * 100).reset_index(name='win_rate').fillna(0)
    win_rate_sector = win_rate_sector.sort_values(by='win_rate', ascending=True)
    
    fig4 = px.bar(win_rate_sector, x='win_rate', y='sector', orientation='h',
                  title="WIN RATES BY SECTOR (%)", height=240,
                  color_discrete_sequence=['#EEEEEE'])
    fig4.update_layout(**layout_config)
    fig4.update_xaxes(**grid_config, title=None)
    fig4.update_yaxes(**grid_config, title=None)
    st.plotly_chart(fig4, width='stretch')
