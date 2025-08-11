import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="Hotel Booking Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #A23B72;
        margin: 1.5rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Load your CSV file
    try:
        df = pd.read_csv('hotel_clean.csv')
        return df
    except:
        # Sample data jika file tidak ada
        np.random.seed(42)
        
        months = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
        
        countries = ['PRT', 'GBR', 'FRA', 'ESP', 'DEU', 'ITA', 'IRL', 'BEL', 'BRA', 'NLD']
        
        market_segments = ['Online TA', 'Offline TA/TO', 'Groups', 'Direct', 'Corporate', 
                          'Complementary', 'Aviation', 'Undefined']
        
        hotels = ['Sheraton Lima Hotel & Convention Center Lima, Peru',
                  'Renaissance New York Times Square Hotel New York, NY',
                  'Orlando Airport Courtyard Orlando, FL',
                  'Waves, Barbados Barbados',
                  'Protea Hotel Fire & Ice! by Marriott Cape Town Cape Town, South Africa']
        
        n_records = 83006
        data = {
            'hotel': np.random.choice(hotels, n_records),
            'is_canceled': np.random.choice([0, 1], n_records, p=[0.63, 0.37]),
            'arrival_date_month': np.random.choice(months, n_records),
            'country': np.random.choice(countries, n_records, 
                                      p=[0.4, 0.1, 0.087, 0.105, 0.061, 0.031, 0.028, 0.02, 0.019, 0.017]),
            'market_segment': np.random.choice(market_segments, n_records, 
                                             p=[0.47, 0.20, 0.17, 0.10, 0.044, 0.006, 0.002, 0.0001]),
            'adr': np.random.normal(100, 50, n_records),
            'total_of_special_requests': np.random.choice([0, 1, 2, 3, 4, 5], n_records,
                                                        p=[0.59, 0.39, 0.088, 0.033, 0.004, 0.0001]),
            'total_guests': np.random.choice([1, 2, 3, 4, 5, 6], n_records,
                                           p=[0.19, 0.69, 0.088, 0.033, 0.001, 0.00001]),
            'price_category': np.random.choice(['Budget', 'Standard', 'Premium'], n_records,
                                             p=[0.31, 0.55, 0.14])
        }
        
        df = pd.DataFrame(data)
        df['adr'] = np.abs(df['adr'])
        return df

def create_monthly_booking_chart(df):
    monthly_stats = df.groupby('arrival_date_month').agg({
        'hotel': 'count',
        'adr': 'mean'
    }).round(1)
    
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_stats = monthly_stats.reindex(month_order)
    
    fig = px.bar(
        x=monthly_stats.index,
        y=monthly_stats['hotel'],
        title='Monthly Booking Volume',
        labels={'x': 'Month', 'y': 'Number of Bookings'},
        color=monthly_stats['hotel'],
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(showlegend=False, height=400, title_x=0.5)
    return fig, monthly_stats

def create_cancellation_analysis(df):
    hotel_cancel = df.groupby('hotel').agg({
        'hotel': 'count',
        'is_canceled': ['sum', 'mean']
    }).round(3)
    
    hotel_cancel.columns = ['total_bookings', 'total_cancellations', 'cancel_rate']
    hotel_cancel['cancel_rate_percent'] = (hotel_cancel['cancel_rate'] * 100).round(1)
    hotel_cancel = hotel_cancel.sort_values('total_cancellations', ascending=False)
    
    return hotel_cancel

def create_country_analysis(df):
    country_stats = df.groupby('country').agg({
        'hotel': 'count',
        'is_canceled': ['sum', 'mean'],
        'adr': 'mean'
    }).round(2)
    
    country_stats.columns = ['total_bookings', 'cancellations', 'cancel_rate', 'avg_adr']
    country_stats['cancel_rate_percent'] = (country_stats['cancel_rate'] * 100).round(1)
    country_stats = country_stats.sort_values('total_bookings', ascending=False)
    
    return country_stats

def create_market_segment_analysis(df):
    market_stats = df.groupby('market_segment').agg({
        'hotel': 'count',
        'adr': 'mean',
        'is_canceled': 'mean'
    }).round(2)
    
    market_stats.columns = ['jumlah_booking', 'rata_rata_harga', 'cancel_rate_persen']
    market_stats['cancel_rate_persen'] = (market_stats['cancel_rate_persen'] * 100).round(1)
    
    market_stats['total_revenue'] = (market_stats['jumlah_booking'] * market_stats['rata_rata_harga']).round(2)
    market_stats['revenue_per_booking'] = market_stats['rata_rata_harga'].round(2)
    
    market_stats = market_stats.sort_values('jumlah_booking', ascending=False)
    
    return market_stats

def create_guest_analysis(df):
    guest_stats = df.groupby('total_guests').agg({
        'hotel': 'count',
        'is_canceled': ['sum', 'mean'],
        'adr': 'mean'
    }).round(2)
    
    guest_stats.columns = ['jumlah_booking', 'cancellations', 'cancel_rate_persen', 'avg_adr']
    guest_stats['cancel_rate_persen'] = (guest_stats['cancel_rate_persen'] * 100).round(1)
    
    return guest_stats

def create_price_category_analysis(df):
    price_stats = df.groupby('price_category').agg({
        'hotel': 'count',
        'is_canceled': 'mean',
        'adr': 'mean'
    }).round(2)
    
    price_stats.columns = ['jumlah_booking', 'cancel_rate_persen', 'rata_rata_harga']
    price_stats['cancel_rate_persen'] = (price_stats['cancel_rate_persen'] * 100).round(1)
    
    return price_stats

def create_special_request_analysis(df):
    df['request_category'] = df['total_of_special_requests'].apply(
        lambda x: 'Tidak ada request' if x == 0 else ('1-2 request' if x <= 2 else '3+ request')
    )
    
    request_stats = df.groupby('request_category').agg({
        'hotel': 'count',
        'is_canceled': ['sum', 'mean'],
        'total_of_special_requests': 'mean'
    }).round(2)
    
    request_stats.columns = ['jumlah_booking', 'cancellations', 'cancel_rate_persen', 'avg_requests']
    request_stats['cancel_rate_persen'] = (request_stats['cancel_rate_persen'] * 100).round(1)
    
    return request_stats

def main():
    st.markdown('<h1 class="main-header">Hotel Booking Analytics Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data...'):
        df = load_data()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bookings", f"{len(df):,}")
    
    with col2:
        cancellation_rate = (df['is_canceled'].mean() * 100)
        st.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")
    
    with col3:
        avg_adr = df['adr'].mean()
        st.metric("Average ADR", f"${avg_adr:.2f}")
    
    with col4:
        unique_countries = df['country'].nunique()
        st.metric("Countries", f"{unique_countries}")
    
    # Section 1: Monthly booking analysis
    st.markdown('<h2 class="section-header">Peningkatan Pendapatan</h2>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Bulan mana yang paling ramai")
        monthly_fig, monthly_stats = create_monthly_booking_chart(df)
        st.plotly_chart(monthly_fig, use_container_width=True)
    
    with col2:
        st.subheader("Top 5 Months")
        top_months = monthly_stats.nlargest(5, 'hotel')
        for idx, (month, data) in enumerate(top_months.iterrows(), 1):
            st.write(f"{idx}. **{month}** - {data['hotel']:,} bookings")
    
    # Section 2: Hotel Cancellation Analysis
    st.markdown('<h2 class="section-header">Hotel mana yang banyak cancel</h2>', 
                unsafe_allow_html=True)
    
    hotel_cancel = create_cancellation_analysis(df)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("TOP 5 HOTELS WITH MOST CANCELLATIONS")
        top_5_cancel = hotel_cancel.head()
        
        for idx, (hotel, data) in enumerate(top_5_cancel.iterrows(), 1):
            hotel_short = hotel.split(',')[0]
            st.write(f"**{idx}. {hotel_short}**")
            st.write(f"   Total Cancellations: {data['total_cancellations']:,}")
            st.write(f"   Cancel Rate: {data['cancel_rate_percent']:.1f}%")
            st.write("---")
    
    with col2:
        st.subheader("Hotel Cancellation Data")
        st.dataframe(
            hotel_cancel[['total_bookings', 'total_cancellations', 'cancel_rate_percent']].head(10),
            use_container_width=True
        )
    
    # Section 3: Country Analysis
    st.markdown('<h2 class="section-header">Negara mana yang paling banyak booking</h2>', 
                unsafe_allow_html=True)
    
    country_stats = create_country_analysis(df)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Top 10 Countries")
        st.dataframe(country_stats.head(10)[['total_bookings', 'cancel_rate_percent']], 
                    use_container_width=True)
    
    with col2:
        fig_country = px.bar(
            x=country_stats.head(10).index,
            y=country_stats.head(10)['total_bookings'],
            title='Top 10 Countries by Booking Volume',
            color=country_stats.head(10)['total_bookings'],
            color_continuous_scale='Viridis'
        )
        fig_country.update_layout(height=400, showlegend=False, title_x=0.5)
        st.plotly_chart(fig_country, use_container_width=True)
    
    # Section 4: Market Segment Analysis
    st.markdown('<h2 class="section-header">Market segment mana yang paling menguntungkan</h2>', 
                unsafe_allow_html=True)
    
    market_stats = create_market_segment_analysis(df)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Market Segment Performance")
        st.dataframe(market_stats[['jumlah_booking', 'rata_rata_harga', 'cancel_rate_persen']], 
                    use_container_width=True)
    
    with col2:
        fig_revenue = px.pie(
            values=market_stats['total_revenue'],
            names=market_stats.index,
            title='Revenue Distribution by Market Segment'
        )
        fig_revenue.update_layout(height=400, title_x=0.5)
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Section 5: Guest Analysis
    st.markdown('<h2 class="section-header">Pengaruh jumlah tamu</h2>', 
                unsafe_allow_html=True)
    
    guest_stats = create_guest_analysis(df)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Guest Count Analysis")
        st.dataframe(guest_stats, use_container_width=True)
    
    with col2:
        fig_guests = px.bar(
            x=guest_stats.index,
            y=guest_stats['jumlah_booking'],
            title='Booking Distribution by Guest Count',
            color=guest_stats['cancel_rate_persen'],
            color_continuous_scale='RdYlBu_r'
        )
        fig_guests.update_layout(height=400, title_x=0.5)
        st.plotly_chart(fig_guests, use_container_width=True)
    
    # Section 6: Price Category Analysis
    st.markdown('<h2 class="section-header">Pengaruh harga terhadap cancellation</h2>', 
                unsafe_allow_html=True)
    
    price_stats = create_price_category_analysis(df)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Price Category Analysis")
        st.dataframe(price_stats, use_container_width=True)
    
    with col2:
        fig_price = px.bar(
            x=price_stats.index,
            y=price_stats['cancel_rate_persen'],
            title='Cancellation Rate by Price Category',
            color=price_stats['cancel_rate_persen'],
            color_continuous_scale='YlOrRd'
        )
        fig_price.update_layout(height=400, title_x=0.5)
        st.plotly_chart(fig_price, use_container_width=True)
    
    # Section 7: Special Request Analysis
    st.markdown('<h2 class="section-header">Special Request VS Cancellation</h2>', 
                unsafe_allow_html=True)
    
    request_stats = create_special_request_analysis(df)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Special Request Categories")
        st.dataframe(request_stats, use_container_width=True)
    
    with col2:
        fig_requests = px.bar(
            x=request_stats.index,
            y=request_stats['cancel_rate_persen'],
            title='Cancellation Rate by Special Request Category',
            color=request_stats['cancel_rate_persen'],
            color_continuous_scale='Reds'
        )
        fig_requests.update_layout(height=400, title_x=0.5)
        st.plotly_chart(fig_requests, use_container_width=True)

if __name__ == "__main__":
    main()
