import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Siswa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS custom
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1E3A8A;
        padding: 20px;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 5px solid #3B82F6;
    }
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .dataframe {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 DASHBOARD ANALISIS DATA SISWA</h1>
    <p>Data Real-time dari Google Sheets | Update Otomatis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # URL Google Sheets
    st.subheader("Data Source")
    sheets_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRh4LhkQFacXW75S33t0NiaGm4rfPRuhcWJ8y4GPfuDrGNyNY1vD6EVWt3yYfCvOtNz80ywUJSIYriJ/pub?gid=0&single=true&output=csv"
    
    st.info("""
    **Google Sheets URL:**
    ```
    https://docs.google.com/spreadsheet...
    ```
    """)
    
    # Auto-refresh
    st.subheader("Auto Refresh")
    auto_refresh = st.checkbox("Aktifkan Auto-refresh", True)
    refresh_interval = st.slider("Interval (detik)", 30, 300, 60)
    
    # Filter data
    st.subheader("🔍 Filter Data")
    show_all = st.checkbox("Tampilkan Semua Data", True)
    
    if not show_all:
        kelas_filter = st.multiselect(
            "Pilih Kelas:",
            options=["Semua"] + ["X-A", "X-B", "XI-A", "XI-B", "XII-A", "XII-B"],
            default=["Semua"]
        )
    
    # Tombol refresh manual
    if st.button("🔄 Refresh Data Sekarang"):
        st.rerun()

@st.cache_data(ttl=60)  # Cache 60 detik
def load_data(url):
    """Load data dari Google Sheets"""
    try:
        df = pd.read_csv(url)
        st.success(f"✅ Data berhasil dimuat! ({len(df)} records)")
        return df
    except Exception as e:
        st.error(f"❌ Gagal memuat data: {e}")
        return pd.DataFrame()

@st.cache_data
def calculate_metrics(df):
    """Hitung semua metrik analisis"""
    if df.empty:
        return {}
    
    metrics = {
        'total_siswa': len(df),
        'rata_nilai_harian': df['nilai harian'].mean(),
        'rata_nilai_tes': df['nilai tes'].mean(),
        'max_harian': df['nilai harian'].max(),
        'max_tes': df['nilai tes'].max(),
        'min_harian': df['nilai harian'].min(),
        'min_tes': df['nilai tes'].min(),
        'median_harian': df['nilai harian'].median(),
        'median_tes': df['nilai tes'].median(),
        'std_harian': df['nilai harian'].std(),
        'std_tes': df['nilai tes'].std()
    }
    
    # Kategorisasi nilai
    def categorize_nilai(nilai):
        if nilai >= 85:
            return 'A (85-100)'
        elif nilai >= 70:
            return 'B (70-84)'
        elif nilai >= 55:
            return 'C (55-69)'
        elif nilai >= 40:
            return 'D (40-54)'
        else:
            return 'E (0-39)'
    
    df['kategori_harian'] = df['nilai harian'].apply(categorize_nilai)
    df['kategori_tes'] = df['nilai tes'].apply(categorize_nilai)
    
    return metrics, df

def display_metrics(metrics):
    """Tampilkan metrik utama"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👨‍🎓 Total Siswa</h3>
            <h2>{metrics.get('total_siswa', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Rata-rata Harian</h3>
            <h2>{metrics.get('rata_nilai_harian', 0):.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📝 Rata-rata Tes</h3>
            <h2>{metrics.get('rata_nilai_tes', 0):.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Nilai Tertinggi</h3>
            <p>Harian: {metrics.get('max_harian', 0):.2f}</p>
            <p>Tes: {metrics.get('max_tes', 0):.2f}</p>
        </div>
        """, unsafe_allow_html=True)

def create_visualizations(df):
    """Buat visualisasi data"""
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Distribusi", "📊 Perbandingan", "🏆 Ranking", "📋 Detail"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram nilai harian
            fig1 = px.histogram(
                df, 
                x='nilai harian',
                nbins=20,
                title='Distribusi Nilai Harian',
                color_discrete_sequence=['#3B82F6']
            )
            fig1.add_vline(
                x=df['nilai harian'].mean(), 
                line_dash="dash",
                line_color="red",
                annotation_text=f"Rata-rata: {df['nilai harian'].mean():.2f}"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Histogram nilai tes
            fig2 = px.histogram(
                df, 
                x='nilai tes',
                nbins=20,
                title='Distribusi Nilai Tes',
                color_discrete_sequence=['#10B981']
            )
            fig2.add_vline(
                x=df['nilai tes'].mean(), 
                line_dash="dash",
                line_color="red",
                annotation_text=f"Rata-rata: {df['nilai tes'].mean():.2f}"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Pie chart kategori
        col3, col4 = st.columns(2)
        
        with col3:
            fig3 = px.pie(
                df, 
                names='kategori_harian',
                title='Kategori Nilai Harian',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            fig4 = px.pie(
                df, 
                names='kategori_tes',
                title='Kategori Nilai Tes',
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            st.plotly_chart(fig4, use_container_width=True)
    
    with tab2:
        # Scatter plot comparison
        fig5 = px.scatter(
            df,
            x='nilai harian',
            y='nilai tes',
            color='kelas',
            size='nilai harian',
            hover_data=['nama siswa'],
            title='Perbandingan Nilai Harian vs Nilai Tes',
            
        )
        fig5.update_layout(
            xaxis_title="Nilai Harian",
            yaxis_title="Nilai Tes"
        )
        st.plotly_chart(fig5, use_container_width=True)
        
        # Box plot per kelas
        col5, col6 = st.columns(2)
        
        with col5:
            fig6 = px.box(
                df,
                x='kelas',
                y='nilai harian',
                title='Distribusi Nilai Harian per Kelas',
                color='kelas'
            )
            st.plotly_chart(fig6, use_container_width=True)
        
        with col6:
            fig7 = px.box(
                df,
                x='kelas',
                y='nilai tes',
                title='Distribusi Nilai Tes per Kelas',
                color='kelas'
            )
            st.plotly_chart(fig7, use_container_width=True)
    
    with tab3:
        # Top 10 ranking
        st.subheader("🏆 Top 10 Siswa Tertinggi")
        
        df['total_nilai'] = (df['nilai harian'] * 0.6 + df['nilai tes'] * 0.4)
        df_ranking = df.sort_values('total_nilai', ascending=False).head(10)
        df_ranking['peringkat'] = range(1, len(df_ranking) + 1)
        
        st.dataframe(
            df_ranking[['peringkat', 'nama siswa', 'kelas', 'nilai harian', 'nilai tes', 'total_nilai']],
            use_container_width=True
        )
        
        # Bottom 10
        st.subheader("📉 10 Siswa Terendah")
        df_bottom = df.sort_values('total_nilai', ascending=True).head(10)
        df_bottom['peringkat'] = range(len(df), len(df) - 10, -1)
        
        st.dataframe(
            df_bottom[['peringkat', 'nama siswa', 'kelas', 'nilai harian', 'nilai tes', 'total_nilai']],
            use_container_width=True
        )
    
    with tab4:
        # Detail data dengan filter
        st.subheader("📋 Data Lengkap")
        
        # Search
        search_term = st.text_input("🔍 Cari nama siswa:", "")
        
        if search_term:
            filtered_df = df[df['nama siswa'].str.contains(search_term, case=False, na=False)]
        else:
            filtered_df = df
        
        # Tampilkan data
        st.dataframe(
            filtered_df[
                ['nama siswa', 'kelas', 'nilai harian', 'kategori_harian', 
                 'nilai tes', 'kategori_tes', 'total_nilai']
            ].sort_values('total_nilai', ascending=False),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv,
            file_name="data_siswa_filtered.csv",
            mime="text/csv"
        )

def display_statistics(df):
    """Tampilkan statistik detail"""
    st.header("📊 Statistik Detail")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Nilai Harian")
        stats_harian = df['nilai harian'].describe()
        st.write(stats_harian)
        
        st.markdown("**Korelasi dengan Nilai Tes:**")
        correlation = df['nilai harian'].corr(df['nilai tes'])
        st.write(f"Koefisien Korelasi: {correlation:.3f}")
        
        if correlation > 0.7:
            st.success("✅ Korelasi kuat positif")
        elif correlation > 0.3:
            st.info("ℹ️ Korelasi sedang")
        else:
            st.warning("⚠️ Korelasi lemah")
    
    with col2:
        st.subheader("Nilai Tes")
        stats_tes = df['nilai tes'].describe()
        st.write(stats_tes)
        
        st.markdown("**Analisis Per Kelas:**")
        kelas_stats = df.groupby('kelas').agg({
            'nilai harian': ['mean', 'std', 'count'],
            'nilai tes': ['mean', 'std']
        }).round(2)
        
        st.dataframe(kelas_stats, use_container_width=True)

def main():
    """Main application"""
    
    # Load data
    df = load_data(sheets_url)
    
    if df.empty:
        st.warning("Tidak ada data yang dapat dimuat. Periksa koneksi internet atau URL.")
        return
    
    # Hitung metrics
    metrics, df_processed = calculate_metrics(df)
    
    # Tampilkan metrics
    display_metrics(metrics)
    
    # Tabs utama
    tab_main1, tab_main2, tab_main3 = st.tabs(["📈 Visualisasi", "📊 Statistik", "ℹ️ Info"])
    
    with tab_main1:
        create_visualizations(df_processed)
    
    with tab_main2:
        display_statistics(df_processed)
    
    with tab_main3:
        st.header("ℹ️ Informasi Dashboard")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("""
            ### 📋 Fitur Utama
            - **Auto-sync** dengan Google Sheets
            - **Visualisasi interaktif** dengan Plotly
            - **Analisis statistik** lengkap
            - **Filter & search** real-time
            - **Export data** ke CSV
            - **Responsive design**
            
            ### 🔄 Update Data
            Data otomatis update dari Google Sheets.
            Refresh interval dapat diatur di sidebar.
            """)
        
        with col_info2:
            st.markdown("""
            ### 📊 Metrik yang Dihitung
            1. **Statistik Deskriptif:**
               - Mean, Median, Mode
               - Standard Deviation
               - Min/Max values
            
            2. **Analisis Lanjutan:**
               - Korelasi antar variabel
               - Distribusi per kategori
               - Ranking siswa
            
            3. **Visualisasi:**
               - Histogram & Box plot
              
               - Pie chart kategori
            """)
        
        # Last update timestamp
        st.markdown("---")
        st.caption(f"🕐 Terakhir update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":

    main()
