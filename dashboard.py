import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import base64
import streamlit.components.v1 as components
import requests

@st.cache_data(ttl=3600)
def convert_usd_to_eur(amount):
    # Using the latest 2026 endpoint
    url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # The data is nested under the base currency key ('usd')
        rate = data['usd']['eur']
        total = amount * rate
        
        print(f"${amount} USD = {total:.2f} EUR (Rate: {rate})")
        return total
    except Exception as e:
        print(f"Error: {e}")
        return amount * 0.92 # Fallback

@st.cache_data(ttl=3600)
def convert_eur_to_usd(amount):
    # Using the latest 2026 endpoint
    url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # The data is nested under the base currency key ('eur')
        rate = data['eur']['usd']
        total = amount * rate
        
        print(f"€{amount} EUR = {total:.2f} USD (Rate: {rate})")
        return total
    except Exception as e:
        print(f"Error: {e}")
        return amount * 1.08 # Fallback

@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def play_background_music(file_path: str):
    b64 = get_base64_of_bin_file(file_path)
    
    html = f"""
    <audio autoplay loop style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)

def get_base64_data_url(file_path, file_type):
    ext = file_path.split('.')[-1]
    binary_string = get_base64_of_bin_file(file_path)
    return f"data:{file_type}/{ext};base64,{binary_string}"

try:
    bg_img = get_base64_data_url('Background.jpg', 'image')
except Exception:
    bg_img = ""


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Vincent's hobby Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- MOBILE SIDEBAR HACK ---
# Force sidebar to open on mobile (where it defaults to collapsed)
if 'sidebar_opened_once' not in st.session_state:
    st.session_state.sidebar_opened_once = True
    components.html("""
        <script>
            // Wait a bit for the DOM to be ready
            setTimeout(function(){
                // Look for the 'Open Sidebar' button (visible only if collapsed)
                const button = window.parent.document.querySelector('button[data-testid="stSidebarCollapsedControl"]');
                if (button) {
                    button.click();
                }
            }, 500); 
        </script>
    """, height=0)

# --- CUSTOM CSS FOR PREMIUM FEEL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), url("BG_URL_PLACEHOLDER");
        background-size: cover;
        background-attachment: fixed;
        color: #e0e0e0;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(20, 20, 30, 0.8);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Label for collapsed sidebar */
    button[data-testid="stSidebarCollapsedControl"] {
        width: auto !important;
        padding: 0 10px !important;
        background-color: rgba(20, 20, 30, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
    }

    /* Card-like metrics */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(0, 200, 255, 0.4);
    }

    /* Custom Header */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 2rem;
    }

    .glow-text {
        text-shadow: 0 0 10px rgba(0, 200, 255, 0.5);
        color: #ffffff;
        font-weight: 700;
        font-size: 2.5rem;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .glow-text {
            font-size: 1.8rem;
        }
        div[data-testid="metric-container"] {
            margin-bottom: 10px;
        }
        /* Financial data header adjustments */
        .stMarkdown h4 {
            font-size: 1.1rem !important;
            margin-top: 1rem !important;
        }
        /* Spacing for grouped data */
        .stExpander div[data-testid="stVerticalBlock"] > div {
            padding: 2px 0;
        }
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.8rem;
    }
    </style>
""".replace("BG_URL_PLACEHOLDER", bg_img), unsafe_allow_html=True)

# --- APP LOGIC ---

@st.cache_data(ttl=600)
def fetch_stock_data(ticker, period):
    stock = yf.Ticker(ticker)
    # Get historical data
    df = stock.history(period=period)
    # Get info for ratios
    info = stock.info
    return df, info

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Wilder's Smoothing: avg_gain = (prev_avg_gain * (n-1) + current_gain) / n
    # This is equivalent to EMA with alpha = 1 / n
    avg_gain = gain.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Sidebar - Stock Selection
st.sidebar.header("Select Stock")

if 'currency' not in st.session_state:
    st.session_state.currency = 'EUR'



default_stocks = ['GOOG','NVDA','TSLA', 'MSFT', 'HOOD', 'PLTR', 'FIG','MBG.DE', 'VOW3.DE', 'BMW.DE', 'CRWV','COIN', 'META','QBTS']

if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = default_stocks[0]

def handle_custom_ticker():
    ticker = st.session_state.custom_ticker_input.strip().upper()
    if ticker:
        st.session_state.selected_stock = ticker
        st.session_state.custom_ticker_input = "" # Clear the field

def handle_dropdown():
    st.session_state.selected_stock = st.session_state.dropdown_input

# Sync dropdown index with session state
try:
    current_index = default_stocks.index(st.session_state.selected_stock)
except ValueError:
    current_index = 0

st.sidebar.selectbox(
    "interesting stocks", 
    default_stocks, 
    index=current_index, 
    key="dropdown_input", 
    on_change=handle_dropdown
)

st.sidebar.text_input(
    "Or enter any ticker symbol", 
    key="custom_ticker_input", 
    on_change=handle_custom_ticker
)

selected_stock = st.session_state.selected_stock

time_range_map = {
    "1 Day": "1d",
    "5 Days": "5d",
    "1 Month": "1mo",
    "1 Year": "1y",
    "5 Years": "5y",
    "10 Years": "10y"
}
time_range_options = list(time_range_map.keys())
# Use session state to persist value when widget is moved/rerun
if 'time_horizon' not in st.session_state:
    st.session_state.time_horizon = time_range_options[2] # Default to 1 Month

# Sync with the widget's session state if it exists
if 'time_horizon_widget' in st.session_state and st.session_state.time_horizon_widget:
    st.session_state.time_horizon = st.session_state.time_horizon_widget

selected_range_label = st.session_state.time_horizon
selected_period = time_range_map[selected_range_label]


# Music Control
if 'music_playing' not in st.session_state:
    st.session_state.music_playing = False

if st.button("MUSIC"):
    st.session_state.music_playing = not st.session_state.music_playing

if st.session_state.music_playing:
    play_background_music("knowme.mp3")

# Main Title
st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <h2 style="color: rgba(255,255,255,0.7); font-weight: 300; letter-spacing: 2px;">Select stock in sidebar</h2>
    </div>
""", unsafe_allow_html=True)

# Placeholder for header
header_placeholder = st.empty()
header_placeholder.markdown("""
    <div class="header-container">
        <h1 class="glow-text">Select Your Stock</h1>
    </div>
""", unsafe_allow_html=True)

try:
    with st.spinner(f'Fetching data for {selected_stock}...'):
        df, info = fetch_stock_data(selected_stock, selected_period)
        # Check if source currency is EUR (specific to these German stocks)
        eur_stocks = ['MBG.DE', 'VOW3.DE', 'BMW.DE']
        if selected_stock in eur_stocks:
            # Normalize price data to USD so the rest of the app works predictably
            usd_rate = convert_eur_to_usd(1.0)
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = df[col] * usd_rate
            #print(f"Normalized {selected_stock} from EUR to USD using rate {usd_rate}")

        company_name = info.get('longName', selected_stock)
        header_placeholder.markdown(f"""
            <div class="header-container">
                <h1 class="glow-text">{company_name}</h1>
            </div>
        """, unsafe_allow_html=True)

    if df.empty:
        st.error("No data found for this ticker and period.")
    else:
        # Layout: Top Row Metrics
        col1, col2, col3 = st.columns(3)
        
        # Current Price
        current_price = df['Close'].iloc[-1]
        prev_price = df['Open'].iloc[0]

        # Currency conversion for chart
        display_df = df.copy()
        currency_label = "Euro" if st.session_state.currency == "EUR" else "USD"
        currency_symbol = "€" if st.session_state.currency == "EUR" else "$"
        
        if st.session_state.currency == "EUR":
            rate = convert_usd_to_eur(1.0)
            for col in ['Open', 'High', 'Low', 'Close']:
                display_df[col] = display_df[col] * rate
            display_price = current_price * rate
        else:
            display_price = current_price

        # Ensure only Monday to Friday (dayofweek < 5: 0=Mon, 4=Fri)
        display_df = display_df[display_df.index.dayofweek < 5]

        price_change = current_price - prev_price
        pct_change = (price_change / prev_price) * 100

        col1.metric("Current Price", f"{currency_symbol}{display_price:,.2f}", f"{pct_change:+.2f}%")
        
        # Financial Data requested: PE ratio, peg ratio, eps
        pe_ratio = info.get('forwardPE', 'N/A')
        if pe_ratio != 'N/A': pe_ratio = f"{pe_ratio:.2f}"
        
        peg_ratio = info.get('pegRatio', 'N/A')
        if peg_ratio != 'N/A': peg_ratio = f"{peg_ratio:.2f}"
        
        eps = info.get('trailingEps', 'N/A')
        if eps != 'N/A': eps = f"${eps:.2f}"

        # col2.metric("EPS (Trailing)", eps)

        # Plotly Chart
        chart_title_col, chart_btn_col = st.columns([0.8, 0.2])
        with chart_title_col:
            st.markdown(f"### Market Movement [{currency_symbol}]")
        with chart_btn_col:
            btn_label = "Switch to $" if st.session_state.currency == "EUR" else "Switch to €"
            if st.button(btn_label):
                st.session_state.currency = "USD" if st.session_state.currency == "EUR" else "EUR"
                st.rerun()
        
        # Calculate RSI
        display_df['RSI'] = calculate_rsi(display_df)

        # Create subplots: Row 1 = Candlestick (70%), Row 2 = RSI (30%)
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.05, 
            row_heights=[0.7, 0.3],
            subplot_titles=("", "")
        )

        # Add Candlestick trace to Row 1
        fig.add_trace(go.Candlestick(
            x=display_df.index,
            open=display_df['Open'],
            high=display_df['High'],
            low=display_df['Low'],
            close=display_df['Close'],
            name=f"{selected_stock} Price",
            increasing_line_color='#00ffcc', 
            decreasing_line_color='#ff4d4d'
        ), row=1, col=1)

        # Add RSI trace to Row 2
        fig.add_trace(go.Scatter(
            x=display_df.index,
            y=display_df['RSI'],
            name='RSI',
            line=dict(color='#ffcc00', width=2),
            hovertemplate='%{y:.2f}'
        ), row=2, col=1)

        # Add horizontal lines for RSI overbought (70) and oversold (30) levels
        fig.add_hline(y=70, line_dash="dash", line_color="rgba(255, 77, 77, 0.5)", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgba(0, 255, 204, 0.5)", row=2, col=1)

        # Calculate dynamic y-axis range for Price chart
        y_min = display_df['Low'].min()
        y_max = display_df['High'].max()
        padding = (y_max - y_min) * 0.1 if y_max > y_min else y_min * 0.1
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='rgba(255,255,255,0.5)')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.05)',
                showline=False,
                tickfont=dict(color='rgba(255,255,255,0.5)'),
                side='right',
                range=[y_min - padding, y_max + padding],
                tickprefix=currency_symbol,
                fixedrange=True
            ),
            # RSI y-axis styling
            yaxis2=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.05)',
                showline=False,
                tickfont=dict(color='rgba(255,255,255,0.5)'),
                side='right',
                range=[0, 100],
                tickvals=[30, 70],
                title="RSI (14)",
                fixedrange=True
            ),
            xaxis_rangebreaks=[
                dict(bounds=["sat", "mon"]), # hide weekends
            ],
            margin=dict(l=0, r=0, t=20, b=0),
            height=650, # Increased height to accommodate the extra chart
            xaxis_rangeslider_visible=False,
            hovermode="x unified",
            showlegend=False
        )

        st.plotly_chart(fig, width='stretch')

        # Time Horizon Selection directly under chart
        st.markdown("<div style='display: flex; justify-content: center; margin-top: -15px; margin-bottom: 25px;'>", unsafe_allow_html=True)
        st.session_state.time_horizon = st.segmented_control(
            "Select Time Horizon",
            options=time_range_options,
            default=st.session_state.time_horizon,
            key="time_horizon_widget",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Additional Info
        with st.expander("ℹ️ Company Profile"):
            st.write(info.get('longBusinessSummary', 'No summary available.'))

        # --- Key Financial Data Section ---
        with st.expander("📊 Key Financial Data", expanded=True):
            def format_val(val, unit="", multiplier=1, is_percent=False):
                if val is None or val == "N/A": return "N/A"
                try:
                    num = float(val) * multiplier
                    if is_percent:
                        return f"{num*100:.2f}%"

                    # Auto-scale large numbers
                    abs_num = abs(num)
                    if abs_num >= 1e12:
                        return f"${num/1e12:.2f} Trillion"
                    elif abs_num >= 1e9:
                        return f"${num/1e9:.2f} Billion"
                    elif abs_num >= 1e6:
                        return f"${num/1e6:.2f} Million"
                    
                    # Fallback for smaller numbers
                    return f"{num:,.2f} {unit}".strip()
                except:
                    return "N/A"

            def format_date(timestamp):
                if timestamp is None or timestamp == "N/A": return "N/A"
                try:
                    return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y')
                except:
                    return "N/A"

            f_col1, f_col2 = st.columns(2)

            with f_col1:
                st.markdown("#### 💰 Valuation & Metrics")
                st.write(f"**Market Cap:** {format_val(info.get('marketCap'))}")
                st.write(f"**Trailing P/E:** {format_val(info.get('trailingPE'))}")
                st.write(f"**Forward P/E:** {format_val(info.get('forwardPE'))}")
                st.write(f"**PEG Ratio:** {format_val(info.get('trailingPegRatio', info.get('pegRatio')))}")
                st.write(f"**Trailing EPS:** {format_val(info.get('trailingEps'), '$')}")
                st.write(f"**Short Ratio:** {format_val(info.get('shortRatio'))}")

                st.markdown("#### 📈 Growth & Targets")
                st.write(f"**Earnings Growth:** {format_val(info.get('earningsGrowth'), is_percent=True)}")
                st.write(f"**Quarterly Earnings Growth:** {format_val(info.get('earningsQuarterlyGrowth'), is_percent=True)}")
                st.write(f"**Revenue Growth:** {format_val(info.get('revenueGrowth'), is_percent=True)}")
                st.write(f"**Target High:** {format_val(info.get('targetHighPrice'), '$')}")
                st.write(f"**Target Mean:** {format_val(info.get('targetMeanPrice'), '$')}")
                st.write(f"**Target Low:** {format_val(info.get('targetLowPrice'), '$')}")
                st.write(f"**Next Earnings Date:** {format_date(info.get('earningsTimestampStart'))}")

            with f_col2:
                st.markdown("#### 💵 Income & Returns")
                st.write(f"**Total Revenue:** {format_val(info.get('totalRevenue'))}")
                st.write(f"**EBITDA:** {format_val(info.get('ebitda'))}")
                st.write(f"**Gross Profits:** {format_val(info.get('grossProfits'))}")
                st.write(f"**Gross Margins:** {format_val(info.get('grossMargins'), is_percent=True)}")
                st.write(f"**Operating Margins:** {format_val(info.get('operatingMargins'), is_percent=True)}")
                st.write(f"**Profit Margins:** {format_val(info.get('profitMargins'), is_percent=True)}")

                st.markdown("#### 🏦 Cash & Debt")
                st.write(f"**Total Cash:** {format_val(info.get('totalCash'))}")
                st.write(f"**Total Debt:** {format_val(info.get('totalDebt'))}")
                st.write(f"**Debt to Equity:** {format_val(info.get('debtToEquity'), multiplier=0.01)}")
                st.write(f"**Free Cashflow:** {format_val(info.get('freeCashflow'))}")
                st.write(f"**Operating Cashflow:** {format_val(info.get('operatingCashflow'))}")

        # --- Company Officers Section ---
        st.markdown("### 👔 Key Leadership")
        if st.checkbox("Show Company Officers"):
            # Ensure the key exists and has data
            if 'companyOfficers' in info and info['companyOfficers']:
                officers = info['companyOfficers']
                officer_list = []
                
                for officer in officers:
                    # Build a dictionary only with available data
                    row = {}
                    if 'name' in officer:
                        row["Name"] = officer['name']
                    if 'title' in officer:
                        row["Title"] = officer['title']
                    if 'age' in officer:
                        row["Age"] = officer['age']
                    
                    # Handle Pay specifically (only if present and non-zero)
                    if 'totalPay' in officer and officer['totalPay']:
                        row["Total Pay (M)"] = f"${officer['totalPay']/1_000_000:.2f}"
                    
                    if row: # Only add if we actually found some data for this person
                        officer_list.append(row)

                if officer_list:
                    # Convert to DataFrame for a clean UI table
                    df_officers = pd.DataFrame(officer_list)
                    st.dataframe(df_officers, width='stretch', hide_index=True)
                else:
                    st.info("No detailed officer metrics found.")
            else:
                st.info("Leadership information is not available for this ticker.")
            
except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")

st.markdown("""
    <div class="footer">
        • Created by Vincent
    </div>
""", unsafe_allow_html=True)
