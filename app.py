import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Konfigurasi
st.set_page_config(page_title="Analisis Siswa", layout="wide")

# Load data
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRh4LhkQFacXW75S33t0NiaGm4rfPRuhcWJ8y4GPfuDrGNyNY1vD6EVWt3yYfCvOtNz80ywUJSIYriJ/pub?gid=0&single=true&output=csv"
    return pd.read_csv(url)

def main():
    st.title("📊 Analisis Data Siswa")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("Data tidak dapat dimuat")
        return
    
    st.success(f"✅ Data dimuat: {len(df)} siswa")
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 Pencarian")
        search = st.text_input("Cari siswa:")
        
        st.header("⚙️ Filter")
        show_all = st.checkbox("Tampilkan semua", True)
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Siswa", len(df))
    
    with col2:
        st.metric("Rata Nilai Harian", f"{df['nilai harian'].mean():.2f}")
    
    with col3:
        st.metric("Rata Nilai Tes", f"{df['nilai tes'].mean():.2f}")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Data", "📈 Grafik", "🔍 Pencarian"])
    
    with tab1:
        st.dataframe(df, use_container_width=True)
        
        # Statistik
        st.subheader("Statistik")
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.write("**Nilai Harian**")
            st.write(df['nilai harian'].describe())
        
        with col_stat2:
            st.write("**Nilai Tes**")
            st.write(df['nilai tes'].describe())
    
    with tab2:
        # Simple matplotlib charts
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Histogram nilai harian
        ax1.hist(df['nilai harian'], bins=10, edgecolor='black', alpha=0.7)
        ax1.axvline(df['nilai harian'].mean(), color='red', linestyle='--')
        ax1.set_title('Distribusi Nilai Harian')
        ax1.set_xlabel('Nilai')
        ax1.set_ylabel('Frekuensi')
        
        # Histogram nilai tes
        ax2.hist(df['nilai tes'], bins=10, edgecolor='black', alpha=0.7, color='green')
        ax2.axvline(df['nilai tes'].mean(), color='red', linestyle='--')
        ax2.set_title('Distribusi Nilai Tes')
        ax2.set_xlabel('Nilai')
        ax2.set_ylabel('Frekuensi')
        
        st.pyplot(fig)
        
        # Box plot
        fig2, ax3 = plt.subplots(figsize=(10, 4))
        data_to_plot = [df['nilai harian'], df['nilai tes']]
        ax3.boxplot(data_to_plot, labels=['Nilai Harian', 'Nilai Tes'])
        ax3.set_title('Box Plot Nilai')
        st.pyplot(fig2)
    
    with tab3:
        st.header("Pencarian Siswa")
        
        if search:
            results = df[df['nama siswa'].str.contains(search, case=False, na=False)]
            
            if not results.empty:
                st.success(f"Ditemukan {len(results)} siswa:")
                st.dataframe(results, use_container_width=True)
                
                # Detail siswa
                selected = st.selectbox("Pilih siswa:", results['nama siswa'].tolist())
                
                if selected:
                    student = df[df['nama siswa'] == selected].iloc[0]
                    
                    st.markdown(f"### 👤 {selected}")
                    col_s1, col_s2, col_s3 = st.columns(3)
                    
                    with col_s1:
                        st.metric("Kelas", student['kelas'])
                    
                    with col_s2:
                        st.metric("Nilai Harian", f"{student['nilai harian']:.2f}")
                    
                    with col_s3:
                        st.metric("Nilai Tes", f"{student['nilai tes']:.2f}")
            else:
                st.warning("Siswa tidak ditemukan")
        else:
            st.info("Masukkan nama siswa di sidebar untuk mencari")
    
    # Footer
    st.markdown("---")
    st.caption(f"Terakhir update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
