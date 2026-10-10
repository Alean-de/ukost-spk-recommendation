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