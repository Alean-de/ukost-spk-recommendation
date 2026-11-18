#  UKOST: Sistem Pengambilan Keputusan Kost Berdasarkan Preferensi Mahasiswa Ukrida

Ukost (Ukrida Kost) merupakan platform berbasis website untuk membantu Mahasiswa Ukrida yang merantau atau pun tidak, untuk menemukan tempat tinggal yang sesuai dengan biaya dan jarak ke Ukrida Kampus 1 yang terletak di *Tanjung Duren* dan Kampus 2 yang terletak di *Duri Kepa*. 

## Overview
Mencari tempat tinggal di sekitar kampus sering kali menjadi proses yang menyita waktu dan membingungkan bagi mahasiswa UKRIDA, terutama karena banyaknya variasi harga, fasilitas, serta jarak ke lokasi perkuliahan.

Sebagai solusinya, U KOST hadir sebagai aplikasi berbasis Sistem Pendukung Keputusan (SPK) yang dirancang untuk membantu mahasiswa memfilter dan membandingkan berbagai opsi kost secara otomatis dan objektif sesuai dengan kebutuhan serta preferensi mereka.

Dengan adanya sistem ini, diharapkan mahasiswa dapat menemukan hunian yang paling tepat dengan lebih cepat, efisien, dan transparan tanpa harus melakukan pencarian manual yang rumit.

## Features
Fitur-fitur pada website ini yaitu:
- Login dengan menggunakan email civitas ukrida
- Input preferensi untuk menemukan kost yang sesuai dengan kebutuhan user
- Komparasi 3 kost berdasarkan output yang diberikan sistem
- Fitur "Favorit" untuk menyimpan data kost yang diminati untuk diakses kembali

Seluruh fitur ini masih berada dalam tahap pengembangan.

## Tech Stack
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)

## Formulas
Untuk menghasilkan rekomendasi kost yang akurat dan sesuai dengan preferensi pengguna, sistem memerlukan kerangka komputasi yang terstruktur. Proses pengambilan keputusan multi-kriteria ini diselesaikan melalui beberapa tahapan perhitungan matematis. Berikut adalah rincian rumus dan tahapan sistematis yang digunakan dalam perancangan model:
    
1. Pembobotan Survei
    
    a. Rata-rata skor kriteria j
       $$s_j = \frac{\sum_{k=1}^{n} x_{kj}}{n}$$
    dengan $x_{kj}$ adalah skor yang diberikan responden ke-$k$ pada kriteria ke-$j$.

    b. Pemecahan bobot jarak berdasarkan proporsi responden

    Kriteria jarak dipecah menjadi dua kolom (C8 = jarak ke Kampus 1, C9 = jarak ke Kampus 2). Agar jarak tidak terhitung dua kali, skor tiap kampus dikalikan proporsi respondennya.

    $$p_{K1} = \frac{n_{K1}}{n}, \qquad p_{K2} = \frac{n_{K2}}{n}$$

    $$s'_{C8} = s_{C8} \times p_{K1}, \qquad s'_{C9} = s_{C9} \times p_{K2}$$

    Untuk kriteria C1 sampai C7 berlaku $s'_j = s_j$.

    c. Normalisasi bobot

    $$w_j = \frac{s'_j}{\sum_{j=1}^{n} s'_j}, \qquad \sum_{j=1}^{n} w_j = 1$$

    Keterangan:
    - $s_j$ : rata-rata skor kepentingan kriteria ke-$j$
    - $n$ : jumlah responden
    - $n_{K1}, n_{K2}$ : jumlah responden Kampus 1 dan Kampus 2
    - $p_{K1}, p_{K2}$ : proporsi responden tiap kampus
    - $s'_j$ : skor yang sudah disesuaikan
    - $w_j$ : bobot akhir kriteria ke-$j$

2. Matriks Keputusan

    Matriks keputusan $X$ berukuran $m \times n$, dengan $m$ adalah jumlah alternatif kost dan $n$ jumlah kriteria.

    $$X = \begin{bmatrix} x_{11} & x_{12} & \cdots & x_{1n} \\ x_{21} & x_{22} & \cdots & x_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ x_{m1} & x_{m2} & \cdots & x_{mn} \end{bmatrix}$$

    Keterangan:
    - $x_{ij}$ : nilai alternatif ke-$i$ pada kriteria ke-$j$
    - Fasilitas (C1–C6) dikonversi menjadi biner: tersedia (TRUE) = 1, tidak tersedia (FALSE) = 0
    - Harga (C7) dalam rupiah, jarak (C8 dan C9) dalam meter
    - Benefit (C1–C6): semakin besar semakin baik
    - Cost (C7–C9): semakin kecil semakin baik

3. Normalisasi Matriks

    Setiap nilai dinormalisasi dengan metode vektor agar semua kriteria berada pada skala yang sebanding.

    $$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{i=1}^{m} x_{ij}^2}}$$

4. Matriks Ternormalisasi Terbobot

    $$y_{ij} = w_j \times r_{ij}$$

5. Solusi Ideal Positif ($A^+$) dan Negatif ($A^-$)

    Untuk kriteria benefit:
    $$A^+_j = \max_i(y_{ij}), \qquad A^-_j = \min_i(y_{ij})$$

    Untuk kriteria cost:
    $$A^+_j = \min_i(y_{ij}), \qquad A^-_j = \max_i(y_{ij})$$

6. Jarak ke Solusi Ideal

    $$D_i^+ = \sqrt{\sum_{j=1}^{n} \left(y_{ij} - A_j^+\right)^2}$$

    $$D_i^- = \sqrt{\sum_{j=1}^{n} \left(y_{ij} - A_j^-\right)^2}$$

7. Nilai Preferensi dan Ranking

    $$V_i = \frac{D_i^-}{D_i^+ + D_i^-}, \qquad 0 \le V_i \le 1$$

    Alternatif dengan nilai $V_i$ terbesar berada di peringkat pertama dan menjadi rekomendasi utama.

## Alasan Pemilihan Metode TOPSIS

TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) dipilih karena:
- Mampu menangani banyak kriteria sekaligus, baik benefit maupun cost, sesuai kasus pemilihan kost (fasilitas, harga, jarak).
- Bobot kriteria dapat diambil langsung dari data survei, sehingga hasil mencerminkan preferensi pengguna.
- Konsepnya jelas: alternatif terbaik adalah yang paling dekat dengan kondisi ideal dan paling jauh dari kondisi terburuk.
- Menghasilkan nilai preferensi numerik sehingga ranking mudah diinterpretasikan.
- Perhitungannya dapat direplikasi sepenuhnya dengan formula spreadsheet.

## Instalation & Setup
1. **Clone repository ini ke lokal**
    ```text
    > git clone https://github.com/Alean-de/ukost-spk-recommendation
    ```
2. **Buat dan Aktifkan Virtual Environment**
    - Windows
        ```text
        > python -m venv venv
        > venv\Scripts\activate
        ```
    - MacOS/Linux
        ```text
        > python3 -m venv venv
        > source venv/bin/activate
        ```
- Install Dependencies
    ```text
    > pip install -r requirements.txt
    ```
- Konfigurasi Database 
    - Nyalakan XAMPP/Laragon (Pastikan MySQL juga aktif)
    - Buat database baru dengan nama yang sesuai di konfigurasi
- Migrasi database
    ```text
    > python manage.py makemigrations
    > python manage.py migrate
    ```
- Jalankan Server Lokal
    ```text
    > py manage.py runserver
    ```
    Buka http://127.0.0.1:8000 di browser Anda.
## Usage
1. Buka aplikasi di browser, kemudian daftarkan diri anda terlebih dahulu melalui menu register atau login dengan email civitas ukrida
2. Masuk ke halaman Masuk ke halaman pencarian dan tentukan kriteria dan bobot yang Anda inginkan (seperti range harga, fasilitas wajib, dan jarak maksimal ke kampus)
3. Klik tombol **Cari**, dan sistem akan memproses serta memeringkat pilihan kost yang paling sesuai
4. Pilih hingga 3 kost dari output yang diberikan oleh sistem untuk dibandingkan secara langsung, atau simpan ke daftar **Favorit** Anda.

## Project Structure
```text
ukost-spk-recommendation/
├── config/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── static/
│   ├── css/
│   ├── images/
│   └── js/
│
├── templates/
│   ├── archive/
│   ├── auth/
│   ├── comparison/
│   ├── home/
│   ├── kost/
│   ├── recommendation/
│   ├── search/
│   └── base.html
│
├── ukost/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── mock_data.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .env
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt

```
## Directory Description
- `config/`: Konfigurasi utama proyek Django (seperti pengaturan settings.py, urls.py, dan wsgi/asgi).
- `static/`: File-file statis seperti gambar, CSS, dan JavaScript untuk tampilan antarmuka.
- `templates/`: Folder yang menyimpan file HTML untuk tampilan antarmuka website.
- `ukost/`: Direktori aplikasi (app) utama Django untuk mengelola logika bisnis sistem rekomendasi kost.
- `.env`: Menyimpan environment variable dan data rahasia secara lokal (seperti secret key dan konfigurasi database).
- `manage.py`: Skrip utilitas baris perintah Django untuk menjalankan server, migrasi database, dan perintah pengelolaan lainnya.
- `requirements.txt`: Daftar pustaka atau library Python yang dibutuhkan agar proyek dapat berjalan.

## Contributor & License
- Aleandro Putra Febrianus Giawa (412024044) - Backend Developer & Database
- Jonathan Agustinus Harlim (412024042) - Frontend Developer & UI/UX Design
- Michella Pangkawira (412025024) - 
- Amelia (412025035) -
- Emeli Stevani Tambunan (412025033) -