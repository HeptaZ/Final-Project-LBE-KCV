# Final Project LBE KCV - Prediksi Status Banjir Berdasarkan Parameter Cuaca dari BMKG Menggunakan Algoritma Logistic Regression, Decision Tree, dan KNN

---

## Sumber Dataset

* **Dataset:** [Climate and Flood Jakarta](https://www.kaggle.com/datasets/christopherrichardc/climate-and-flood-jakarta/) (Kaggle)
* **Deskripsi:** Dataset ini berisi data historis parameter iklim/cuaca harian seperti temperatur, kelembapan, curah hujan, kecepatan angin, arah angin, dan durasi penyinaran matahari beserta label kejadian banjir di wilayah DKI Jakarta.

---

## Struktur Repositori

```text
├── FP_LBE_KCV.ipynb     # Jupyter Notebook utama alur Machine Learning
├── data_finish.csv      # File dataset cuaca & banjir
├── requirements.txt     # Daftar dependensi pustaka Python
├── README.md            # Dokumentasi proyek
└── website/             # Folder web dashboard aplikasi (opsional)
```

### Rincian File:
1. **`FP_LBE_KCV.ipynb`**: File Jupyter Notebook utama yang memuat alur lengkap eksperimen Machine Learning (EDA, Preprocessing Pipeline, Penanganan Class Imbalance dengan SMOTE, Feature Scaling, Hyperparameter Tuning GridSearchCV, serta Evaluasi Model).
2. **`data_finish.csv`**: File input dataset cuaca historis yang wajib tersedia pada direktori yang sama untuk keperluan eksekusi kode dan demo presentasi.
3. **`requirements.txt`**: File konfigurasi dependensi Python yang memuat pustaka pendukung seperti `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, dan `imbalanced-learn`.

---

## Panduan & Cara Menjalankan

### 1. Instalasi Dependensi
Pastikan telah menginstal Python (disarankan Python 3.8+). Pasang seluruh pustaka yang diperlukan dengan menjalankan perintah:

```bash
pip install -r requirements.txt
```

### 2. Membuka Notebook (`FP_LBE_KCV.ipynb`)
Notebook dapat dibuka dan dijalankan melalui beberapa alternatif platform:

* **Jupyter Notebook / JupyterLab:**
  ```bash
  jupyter notebook FP_LBE_KCV.ipynb
  ```
* **Visual Studio Code (VS Code):**
  Buka folder repositori di VS Code, pilih file `FP_LBE_KCV.ipynb`, dan pastikan ekstensi **Jupyter** dan **Python** telah aktif.
* **Google Colab:**
  Unggah file `FP_LBE_KCV.ipynb` dan `data_finish.csv` ke dalam sesi Google Colab Anda.

---

> ### Peringatan Penting (Input Dataset)
> File **`data_finish.csv` WAJIB berada di dalam satu folder (direktori kerja) yang sama** dengan file **`FP_LBE_KCV.ipynb`**. Jika file dataset tidak berada di direktori yang sama, pembacaan data (`pd.read_csv('data_finish.csv')`) akan menghasilkan pesan *error (FileNotFoundError)*.

---

## Tahapan Eksperimen Machine Learning

1. **Exploratory Data Analysis (EDA):**
   - Pemeriksaan bentuk dataset (`shape`), nilai hilang (`missing values`), dan tipe data.
   - Analisis distribusi kelas target banjir serta fitur cuaca (Histplot, Countplot, Boxplot).
   - Penanganan nilai hilang (`dropna`) dan konversi derajat arah angin (`0-360°`) ke kategori arah mata angin (N, NE, E, SE, S, SW, W, NW).

2. **Preprocessing Pipeline (`sklearn.pipeline.Pipeline`):**
   - `DateEncoder`: Ekstraksi fitur tanggal menjadi bulan, hari, tahun, dan hari dalam minggu.
   - `ArahAnginAvgEncoder` & `ArahAnginMaxEncoder`: One-Hot Encoding pada fitur arah angin.
   - `NamaDaerahEncoder`: One-Hot Encoding pada fitur nama daerah.
   - `FeatureDropper`: Menghapus kolom identifikasi stasiun (`id_stasiun`, `nama_stasiun`).

3. **Data Splitting & Balancing:**
   - Pemisahan data latih dan data uji menggunakan `StratifiedShuffleSplit` (80% Train, 20% Test, `random_state=42`).
   - Penyeimbangan distribusi kelas target pada data latih menggunakan teknik **SMOTE** (*Synthetic Minority Over-sampling Technique*).

4. **Penskalaan Fitur (*Feature Scaling*):**
   - `StandardScaler` diaplikasikan pada fitur data latih dan uji untuk model yang sensitif terhadap skala fitur (**KNN** dan **Logistic Regression**). Model **Decision Tree** menggunakan data tanpa standarisasi.

5. **Pelatihan & Hyperparameter Tuning:**
   - Pencarian parameter optimal menggunakan `GridSearchCV` dengan 5-Fold Cross Validation dan metrik scoring `f1_weighted`.
   - Model yang dievaluasi:
     - **K-Nearest Neighbors (KNN)**
     - **Logistic Regression**
     - **Decision Tree**

6. **Evaluasi Model:**
   - Evaluasi performa model pada data uji menggunakan metrik: **Accuracy**, **Precision (Weighted)**, **Recall (Weighted)**, dan **F1-Score (Weighted)**.
   - Visualisasi hasil prediksi menggunakan **Confusion Matrix** (Heatmap Seaborn).

---