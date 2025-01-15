import os
import streamlit as st
import pdfplumber
import pandas as pd
import csv

# Fungsi untuk ekstraksi tabel dari PDF dan menyimpan ke CSV
def extract_data_from_pdf(pdf_path, extracted_csv_path):
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                all_tables.append(table)

    # Proses data tabel ke dalam list
    processed_data = []
    for table in all_tables:
        for row in table:
            processed_data.append(row)

    # Simpan data ke DataFrame pandas
    df = pd.DataFrame(processed_data)

    # Simpan data awal ke CSV (ekstraksi mentah)
    df.to_csv(extracted_csv_path, index=False, header=False)

# Fungsi untuk merapikan data CSV
def clean_csv(input_file):
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        data = [row for row in reader]

    # Merapikan setiap elemen dalam file
    cleaned_data = []
    for row in data:
        cleaned_row = [cell.strip().replace('\n', ' ') for cell in row if cell.strip()]
        
        # Mengecek apakah baris tersebut valid (memiliki cukup banyak kolom yang tidak kosong)
        if len(cleaned_row) >= 8:
            cleaned_data.append(cleaned_row)

    return cleaned_data

# Fungsi untuk mengecek dan menyisakan satu data dari duplikasi berdasarkan kolom pertama dan ketujuh
def check_and_remove_duplicates(df):
    # Mengecek duplikasi berdasarkan kolom 1 (index 0) dan kolom 7 (index 6)
    duplicates = df[df.duplicated(subset=[1, 7], keep=False)]
    if not duplicates.empty:
        # Hapus duplikasi dan sisakan satu
        df_no_duplicates = df.drop_duplicates(subset=[1, 7], keep='first')
        return df_no_duplicates, duplicates
    return df, pd.DataFrame()  # Jika tidak ada duplikasi, kembalikan DataFrame asli

# Membuat UI menggunakan Streamlit
st.set_page_config(page_title="Ekstraktor Tabel PDF", layout="wide")
st.title('🦉 Ekstraktor Tabel PDF, Pembersih, dan Pengecek Duplikasi ⚔️')

# Membuat folder 'temp' jika belum ada
temp_dir = "temp"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Upload file PDF
st.sidebar.header("Unggah PDF 🦉")
pdf_file = st.sidebar.file_uploader('Unggah File PDF', type='pdf')

if pdf_file is not None:
    pdf_path = os.path.join(temp_dir, pdf_file.name)
    
    # Menyimpan file PDF sementara
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getbuffer())

    # Inisialisasi path file CSV
    extracted_csv_path = os.path.join(temp_dir, "extracted_data.csv")

    # Proses ekstraksi dan pembersihan data
    with st.spinner("🦉 Ekstraksi data dari PDF..."):
        extract_data_from_pdf(pdf_path, extracted_csv_path)
    
    with st.spinner("⚔️ Membersihkan data yang diekstraksi..."):
        cleaned_data = clean_csv(extracted_csv_path)

    # Menyimpan data yang sudah dibersihkan ke CSV
    cleaned_csv_path = os.path.join(temp_dir, "cleaned_data.csv")
    df_cleaned = pd.DataFrame(cleaned_data)
    df_cleaned.to_csv(cleaned_csv_path, index=False, header=False)

    st.success("Data berhasil diekstrak dan dibersihkan! 🦉⚔️")

    # Tabs untuk berbagai tampilan
    tab1, tab2, tab3 = st.tabs(["Data Bersih 🦉", "Duplikasi ⚔️", "Unduh 📂"])

    with tab1:
        st.subheader("Data Bersih 🦉")
        st.dataframe(df_cleaned, use_container_width=True)

    try:
        # Mengecek dan menampilkan duplikasi
        df_no_duplicates, duplicates = check_and_remove_duplicates(df_cleaned)
        
        with tab2:
            st.subheader("Duplikasi ⚔️")
            if not duplicates.empty:
                st.warning("Ditemukan data duplikasi! ⚠️")
                st.dataframe(duplicates, use_container_width=True)
            else:
                st.success("Tidak ada duplikasi ditemukan. 🎉")
        
        with tab3:
            st.subheader("Opsi Unduhan 📂")
        
            # Baca kembali file cleaned_data.csv
            with open(cleaned_csv_path, 'r', encoding='utf-8') as f:
                cleaned_csv_content = f.read()
        
            # Baca kembali file no_duplicates_data.csv
            with open(no_duplicates_csv_path, 'r', encoding='utf-8') as f:
                no_duplicates_csv_content = f.read()
        
            # Buat objek BytesIO untuk file CSV
            cleaned_csv_buffer = io.BytesIO(cleaned_csv_content.encode('utf-8'))
            no_duplicates_csv_buffer = io.BytesIO(no_duplicates_csv_content.encode('utf-8'))
        
            # Tombol unduh
            st.download_button(
                "Unduh CSV Data Bersih",
                data=cleaned_csv_buffer,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )
            st.download_button(
                "Unduh CSV Tanpa Duplikasi",
                data=no_duplicates_csv_buffer,
                file_name="no_duplicates_data.csv",
                mime="text/csv"
            )
    except KeyError as e:
        st.error(f"Kesalahan dalam memproses data: {e}")
