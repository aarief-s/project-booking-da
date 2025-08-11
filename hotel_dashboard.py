import streamlit as st
import pandas as pd
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
    # Sample data
    np.random.seed(42)
    
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    
    countries = ['PRT', 'GBR', 'FRA', 'ESP', 'DEU', 'ITA', 'IRL', 'BEL', 'BRA', 'NLD']
    
    market_segments = ['Online TA', 'Offline TA/TO', 'Groups', 'Direct', 'Corporate', 
                      'Complementary', 'Aviation', 'Undefined']
    
    hotels = ['Sheraton Lima Hotel', 'Renaissance New York', 'Orlando Airport Courtyard', 
              'Waves Barbados', 'Protea Hotel Cape Town']
    
    n_records = 83006
    data = {
        'hotel': np.random.choice(hotels, n_records),
        'is_canceled': np.random.choice([0, 1], n_records, p=[0.63, 0.37]),
        'arrival_date_month': np.random.choice(months, n_records),
        'country': np.random.choice(countries, n_records, 
                                  p=[0.4, 0.1, 0.087, 0.105, 0.061, 0.031, 0.028, 0.02, 0.019, 0.017]),
        'market_segment': np.random.choice(market_segments, n_records, 
                                         p=[0.47, 0.20, 0.17, 0.10, 0.044, 0.006, 0.002, 0.0001]),
        'adr': np.abs(np.random.normal(100, 50, n_records)),
        'total_of_special_requests': np.random.choice([0, 1, 2, 3, 4, 5], n_records,
                                                    p=[0.59, 0.39, 0.088, 0.033, 0.004, 0.0001]),
        'total_guests': np.random.choice([1, 2, 3, 4, 5, 6], n_records,
                                       p=[0.19, 0.69, 0.088, 0.033, 0.001, 0.00001]),
        'price_category': np.random.choice(['Budget', 'Standard', 'Premium'], n_records,
                                         p=[0.31, 0.55, 0.14])
    }
    
    df = pd.DataFrame(data)
    return df

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
        monthly_stats = df.groupby('arrival_date_month').size()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        monthly_stats = monthly_stats.reindex(month_order)
        
        # Streamlit built-in bar chart
        st.bar_chart(monthly_stats)
    
    with col2:
        st.subheader("Top 5 Months")
        top_months = monthly_stats.nlargest(5)
        for idx, (month, count) in enumerate(top_months.items(), 1):
            st.write(f"{idx}. **{month}** - {count:,} bookings")
    
    # Section 2: Hotel Cancellation Analysis
    st.markdown('<h2 class="section-header">Hotel mana yang banyak cancel</h2>', 
                unsafe_allow_html=True)
    
    hotel_cancel = df.groupby('hotel').agg({
        'hotel': 'count',
        'is_canceled': ['sum', 'mean']
    }).round(3)
    
    hotel_cancel.columns = ['total_bookings', 'total_cancellations', 'cancel_rate']
    hotel_cancel['cancel_rate_percent'] = (hotel_cancel['cancel_rate'] * 100).round(1)
    hotel_cancel = hotel_cancel.sort_values('total_cancellations', ascending=False)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("TOP 5 HOTELS WITH MOST CANCELLATIONS")
        top_5_cancel = hotel_cancel.head()
        
        for idx, (hotel, data) in enumerate(top_5_cancel.iterrows(), 1):
            st.write(f"**{idx}. {hotel}**")
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
    
    country_stats = df.groupby('country').agg({
        'hotel': 'count',
        'is_canceled': 'mean'
    }).round(2)
    
    country_stats.columns = ['total_bookings', 'cancel_rate']
    country_stats['cancel_rate_percent'] = (country_stats['cancel_rate'] * 100).round(1)
    country_stats = country_stats.sort_values('total_bookings', ascending=False)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Top 10 Countries")
        st.dataframe(country_stats.head(10), use_container_width=True)
    
    with col2:
        st.subheader("Booking Volume by Country")
        st.bar_chart(country_stats.head(10)['total_bookings'])
    
    # Section 4: Market Segment Analysis
    st.markdown('<h2 class="section-header">Market segment mana yang paling menguntungkan</h2>', 
                unsafe_allow_html=True)
    
    market_stats = df.groupby('market_segment').agg({
        'hotel': 'count',
        'adr': 'mean',
        'is_canceled': 'mean'
    }).round(2)
    
    market_stats.columns = ['jumlah_booking', 'rata_rata_harga', 'cancel_rate_persen']
    market_stats['cancel_rate_persen'] = (market_stats['cancel_rate_persen'] * 100).round(1)
    market_stats['total_revenue'] = (market_stats['jumlah_booking'] * market_stats['rata_rata_harga']).round(2)
    market_stats = market_stats.sort_values('jumlah_booking', ascending=False)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Market Segment Performance")
        st.dataframe(market_stats[['jumlah_booking', 'rata_rata_harga', 'cancel_rate_persen']], 
                    use_container_width=True)
    
    with col2:
        st.subheader("Revenue by Market Segment")
        st.bar_chart(market_stats['total_revenue'])
    
    # Section 5: Guest Analysis
    st.markdown('<h2 class="section-header">Pengaruh jumlah tamu</h2>', 
                unsafe_allow_html=True)
    
    guest_stats = df.groupby('total_guests').agg({
        'hotel': 'count',
        'is_canceled': 'mean'
    }).round(2)
    
    guest_stats.columns = ['jumlah_booking', 'cancel_rate_persen']
    guest_stats['cancel_rate_persen'] = (guest_stats['cancel_rate_persen'] * 100).round(1)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Guest Count Analysis")
        st.dataframe(guest_stats, use_container_width=True)
    
    with col2:
        st.subheader("Bookings by Guest Count")
        st.bar_chart(guest_stats['jumlah_booking'])
    
    # Section 6: Price Category Analysis
    st.markdown('<h2 class="section-header">Pengaruh harga terhadap cancellation</h2>', 
                unsafe_allow_html=True)
    
    price_stats = df.groupby('price_category').agg({
        'hotel': 'count',
        'is_canceled': 'mean'
    }).round(2)
    
    price_stats.columns = ['jumlah_booking', 'cancel_rate_persen']
    price_stats['cancel_rate_persen'] = (price_stats['cancel_rate_persen'] * 100).round(1)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Price Category Analysis")
        st.dataframe(price_stats, use_container_width=True)
    
    with col2:
        st.subheader("Cancellation Rate by Price Category")
        st.bar_chart(price_stats['cancel_rate_persen'])

if __name__ == "__main__":
    main()
