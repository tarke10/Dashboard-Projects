import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import datetime
import os

# Set page configuration FIRST
st.set_page_config(page_title="Coffee Shop Overview", page_icon="☕", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS Injection: Cyberpunk Style + ColorHunt Palette ---
# Palette:
# Deep Dark Grey: #222831
# Medium Grey: #393E46
# Vibrant Cyan: #00ADB5
# Off White: #EEEEEE
st.markdown("""
<style>
    /* Reduce top/bottom padding to fit everything without scrolling */
    div.block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Hide Streamlit header (menu and deploy button area) to save space */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* Animated Cyberpunk Background using the ColorHunt greys */
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
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(34, 40, 49, 0.7) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-right: 1px solid rgba(0, 173, 181, 0.3);
    }
    
    /* Text colors - Off White with subtle glow */
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, label, .css-10trblm {
        color: #EEEEEE !important;
        text-shadow: 0px 0px 5px rgba(238, 238, 238, 0.3);
    }
    
    /* Custom KPI Cards - Glassmorphism Medium Grey */
    .kpi-card {
        border-radius: 12px;
        padding: 10px 15px;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(57, 62, 70, 0.5); /* #393E46 with opacity */
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
    
    /* Glowing Neon Borders */
    .kpi-red { border-left: 3px solid #00ADB5; box-shadow: 0 0 10px rgba(0, 173, 181, 0.2); }
    .kpi-blue { border-left: 3px solid #EEEEEE; box-shadow: 0 0 10px rgba(238, 238, 238, 0.2); }
    .kpi-green { border-left: 3px solid #00ADB5; box-shadow: 0 0 10px rgba(0, 173, 181, 0.2); }
    
    /* Sidebar buttons - Neon Cyberpunk styling */
    .btn-blue {
        background: transparent;
        color: #00ADB5;
        padding: 8px;
        border-radius: 20px;
        text-align: center;
        margin-top: 5px;
        font-weight: bold;
        border: 1px solid #00ADB5;
        box-shadow: 0 0 10px rgba(0, 173, 181, 0.4);
        text-shadow: 0 0 5px #00ADB5;
        letter-spacing: 1px;
        transition: 0.2s ease;
    }
    .btn-blue:hover { background: rgba(0, 173, 181, 0.2); }
    
    .btn-green {
        background: transparent;
        color: #EEEEEE;
        padding: 8px;
        border-radius: 20px;
        text-align: center;
        margin-top: 10px;
        font-weight: bold;
        border: 1px solid #EEEEEE;
        box-shadow: 0 0 10px rgba(238, 238, 238, 0.2);
        text-shadow: 0 0 5px rgba(238, 238, 238, 0.5);
        letter-spacing: 1px;
        transition: 0.2s ease;
    }
    .btn-green:hover { background: rgba(238, 238, 238, 0.1); }
    
    /* Small sidebar title */
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
    
    /* Filter container mimic - Glass */
    .status-box {
        background: rgba(57, 62, 70, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(238, 238, 238, 0.1);
        border-left: 3px solid #00ADB5;
        padding: 10px 15px;
        border-radius: 12px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 0 10px rgba(0, 173, 181, 0.2);
    }
    .status-box strong { display: block; margin-bottom: 3px; font-size: 0.8rem; color: #00ADB5; letter-spacing: 1px; text-transform: uppercase; text-shadow: 0 0 5px #00ADB5;}
    
    /* Reduce spacing between st.columns elements */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Let's handle data ingestion. We'll try to load the excel file first,
# but if it's missing during development, we'll fall back to our trusty dummy data generator.
def generate_dummy_data():
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq='h')
    dates = np.random.choice(dates, size=5000, replace=False)
    dates = pd.to_datetime(dates)
    
    data = {
        'transaction_id': np.arange(1, 5001),
        'transaction_date': [d.date() for d in dates],
        'transaction_time': [d.time().strftime("%H:%M:%S") for d in dates],
        'transaction_qty': np.random.randint(1, 6, size=5000),
        'store_id': np.random.choice([1, 2, 3], size=5000),
        'store_location': np.random.choice(['Downtown', 'Uptown', 'Suburbs'], size=5000, p=[0.5, 0.3, 0.2]),
        'product_id': np.random.randint(101, 120, size=5000),
        'unit_price': np.random.uniform(2.5, 6.5, size=5000).round(2),
        'product_category': np.random.choice(['Coffee', 'Tea', 'Bakery', 'Merchandise'], size=5000, p=[0.6, 0.2, 0.15, 0.05]),
    }
    
    df = pd.DataFrame(data)
    product_types = {
        'Coffee': ['Latte', 'Espresso', 'Cappuccino', 'Americano'],
        'Tea': ['Green Tea', 'Black Tea', 'Chai Latte'],
        'Bakery': ['Croissant', 'Muffin', 'Bagel'],
        'Merchandise': ['Mug', 'Beans', 'Tote Bag']
    }
    df['product_type'] = df['product_category'].apply(lambda x: np.random.choice(product_types[x]))
    df['product_detail'] = df['product_type'] + ' - Standard'
    return df

@st.cache_data
def load_data():
    file_path = 'Coffee Shop Sales.xlsx'
    
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
    else:
        df = generate_dummy_data()
        
    df['revenue'] = df['transaction_qty'] * df['unit_price']
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['day_of_week'] = df['transaction_date'].dt.day_name()
    df['month'] = df['transaction_date'].dt.month_name()
    
    df['transaction_time'] = df['transaction_time'].astype(str)
    df['hour'] = df['transaction_time'].str.split(':').str[0].astype(int)
    
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=days_order, ordered=True)
    
    months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    df['month'] = pd.Categorical(df['month'], categories=months_order, ordered=True)
    
    return df

df = load_data()

# Setting up the sidebar for our dashboard controls.
# We want users to be able to filter by location and category easily.
st.sidebar.markdown('<div class="sidebar-title">STARBASE HQ</div>', unsafe_allow_html=True)

selected_location = st.sidebar.selectbox("store_location", ["All"] + list(df['store_location'].unique()))
selected_category = st.sidebar.selectbox("product_category", ["All"] + list(df['product_category'].unique()))

st.sidebar.markdown("<br><p style='font-size:0.85rem; margin-bottom: 0px;'>transaction_year</p>", unsafe_allow_html=True)
year_2022 = st.sidebar.checkbox("2022")
year_2023 = st.sidebar.checkbox("2023", value=True)
year_2024 = st.sidebar.checkbox("2024")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown('<div class="btn-blue">EXECUTE</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="btn-green">COMMUNICATE</div>', unsafe_allow_html=True)

# Apply filters
filtered_df = df.copy()
if selected_location != "All":
    filtered_df = filtered_df[filtered_df['store_location'] == selected_location]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['product_category'] == selected_category]

if filtered_df.empty:
    st.warning("No data for these filters.")
    st.stop()

# Now for the fun part: calculating the top-level metrics.
# These KPI cards give a quick snapshot of how the business is doing right now.
total_orders = filtered_df['transaction_id'].nunique()
total_revenue = filtered_df['revenue'].sum()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns([1, 1, 1, 0.7])

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card kpi-red">
        <div>
            <h2>{total_orders:,}</h2>
            <p>Total Orders</p>
        </div>
        <div style="font-size: 2.5rem; text-shadow: 0 0 10px #00ADB5;">🚀</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div>
            <h2 style="color: #EEEEEE !important; text-shadow: 0 0 10px rgba(238,238,238,0.5);">${avg_order_value:.2f}</h2>
            <p>Avg Order Value</p>
        </div>
        <div style="font-size: 2.5rem; text-shadow: 0 0 10px rgba(238,238,238,0.5);">✨</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <div>
            <h2>${total_revenue:,.0f}</h2>
            <p>Total Revenue</p>
        </div>
        <div style="font-size: 2.5rem; text-shadow: 0 0 10px #00ADB5;">🪐</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown("""
    <div class="status-box">
        <strong>SYS. STATUS</strong>
        <p style="margin:0; opacity:0.9; color: #00ADB5; font-family: monospace;">[OK] Online</p>
        <p style="margin:0; opacity:0.8; color: #EEEEEE; font-family: monospace;">[--] Offline</p>
        <p style="margin:0; opacity:0.8; color: #EEEEEE; font-family: monospace;">[--] Standby</p>
    </div>
    """, unsafe_allow_html=True)

# We need to make sure the Plotly charts match our Cyberpunk aesthetic.
# This config strips out the default backgrounds and applies our neon color sequence.
layout_config = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#EEEEEE', size=10, family="Courier New, monospace"), # Cyberpunk tech font
    margin=dict(l=10, r=10, t=30, b=10)   # Tight margins to fit vertically
)
# Faint glowing gridlines for the cyberpunk tactical display look
grid_config = dict(showgrid=True, gridwidth=1, gridcolor='rgba(0, 173, 181, 0.1)', zeroline=False)

# Custom color sequence exactly mapping to the ColorHunt palette
color_sequence = ['#00ADB5', '#EEEEEE', '#393E46']

# Finally, let's lay out the charts in a nice 3-row grid.
# Using columns to keep everything tight and perfectly fitted to one screen.

row1_col1, row1_col2 = st.columns([1.5, 1])

with row1_col1:
    monthly_rev = filtered_df.groupby('month', observed=False, as_index=False)['revenue'].sum()
    fig1 = px.area(monthly_rev, x='month', y='revenue', title="REV. TRAJECTORY", height=230)
    fig1.update_layout(**layout_config)
    fig1.update_xaxes(**grid_config, title=None)
    fig1.update_yaxes(**grid_config, title=None)
    # Using the Neon Cyan with a glow-like fill
    fig1.update_traces(line_color='#00ADB5', fillcolor='rgba(0, 173, 181, 0.2)', line_width=2)
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    loc_cat_rev = filtered_df.groupby(['store_location', 'product_category'], as_index=False)['revenue'].sum()
    fig2 = px.bar(loc_cat_rev, x='revenue', y='store_location', color='product_category', 
                  orientation='h', title="SECTOR REVENUE", height=230,
                  color_discrete_sequence=['#00ADB5', '#EEEEEE', '#393E46', '#222831'])
    fig2.update_layout(**layout_config, barmode='stack', legend_title_text=None)
    fig2.update_xaxes(**grid_config, title=None)
    fig2.update_yaxes(**grid_config, title=None)
    st.plotly_chart(fig2, use_container_width=True)


row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    day_cat_trans = filtered_df.groupby(['day_of_week', 'product_category'], observed=False, as_index=False)['transaction_id'].count()
    fig3 = px.bar(day_cat_trans, x='day_of_week', y='transaction_id', color='product_category',
                  title="TEMPORAL VOLUME", height=220,
                  color_discrete_sequence=['#393E46', '#00ADB5', '#EEEEEE', '#222831'])
    fig3.update_layout(**layout_config, legend_title_text=None)
    fig3.update_xaxes(**grid_config, title=None)
    fig3.update_yaxes(**grid_config, title=None)
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    cat_rev = filtered_df.groupby('product_category', as_index=False)['revenue'].sum()
    fig4 = px.pie(cat_rev, values='revenue', names='product_category', hole=0.6,
                  title="CATEGORY DIST.", height=220,
                  color_discrete_sequence=['#00ADB5', '#EEEEEE', '#393E46', '#222831'])
    fig4.update_layout(**layout_config)
    st.plotly_chart(fig4, use_container_width=True)


row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    top_prod = filtered_df.groupby('product_type', as_index=False)['revenue'].sum().nlargest(5, 'revenue')
    fig5 = px.bar(top_prod, x='revenue', y='product_type', orientation='h',
                  title="TOP PROTOCOLS", height=200,
                  color_discrete_sequence=['#00ADB5'])
    fig5.update_layout(**layout_config)
    fig5.update_xaxes(**grid_config, title=None)
    fig5.update_yaxes(**grid_config, title=None)
    st.plotly_chart(fig5, use_container_width=True)

with row3_col2:
    hour_trans = filtered_df.groupby('hour', as_index=False)['transaction_id'].count()
    fig6 = px.bar(hour_trans, x='transaction_id', y='hour', orientation='h',
                  title="HOURLY FLUX", height=200,
                  color_discrete_sequence=['#EEEEEE'])
    fig6.update_layout(**layout_config)
    fig6.update_xaxes(**grid_config, title=None)
    fig6.update_yaxes(**grid_config, title=None, tickmode='linear')
    st.plotly_chart(fig6, use_container_width=True)
