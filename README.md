# 🎵 BotDS - Discord Music Bot

Bot Discord modern untuk memutar musik dengan berbagai efek dan fitur canggih. Dibuat dengan Python dan discord.py.

**By: NOEKZ**
**Remake By: HAMDAN**

---

## ✨ Fitur Utama

- 🎶 **Playback Musik** - Putar lagu dari YouTube dan SoundCloud
- 📋 **Antrian Lagu** - Kelola playlist dengan sistem antrian
- 🔁 **Autoplay** - Putar lagu serupa secara otomatis
- 🔊 **Audio Effects** - Bassboost dan Nightcore effects
- 🎚️ **Volume Control** - Atur volume 0-200%
- 🔄 **Loop & Shuffle** - Loop lagu atau acak antrian
- 📊 **Queue Management** - Lihat, hapus, dan kelola antrian
- 🎯 **Modern UI** - Semua response menggunakan Discord Embeds

---

## 📋 Daftar Perintah

### Kontrol Dasar
| Perintah | Deskripsi |
|----------|-----------|
| `!join` | Bot masuk ke voice channel Anda |
| `!leave` | Bot keluar dari voice channel |
| `!play <query>` | Putar lagu berdasarkan nama atau URL YouTube |
| `!pause` | Pause lagu yang sedang diputar |
| `!resume` | Lanjutkan lagu yang di-pause |
| `!skip` | Skip ke lagu berikutnya |
| `!stop` | Hentikan playback dan hapus antrian |

### Manajemen Antrian
| Perintah | Deskripsi |
|----------|-----------|
| `!queue` | Tampilkan daftar lagu dalam antrian |
| `!remove <nomor>` | Hapus lagu dari antrian |
| `!shuffle` | Acak urutan lagu dalam antrian |
| `!playlist <url>` | Load YouTube playlist |

### Efek Audio & Volume
| Perintah | Deskripsi |
|----------|-----------|
| `!volume <level>` | Atur volume (0-200%) |
| `!bassboost <intensity>` | Terapkan efek bassboost |
| `!nightcore` | Terapkan efek nightcore |

### Mode & Status
| Perintah | Deskripsi |
|----------|-----------|
| `!loop` | Toggle loop untuk lagu saat ini |
| `!autoplay` | Toggle autoplay mode |
| `!nowplaying` | Tampilkan lagu yang sedang diputar |
| `!seek <MM:SS>` | Cari ke waktu tertentu (dalam pengembangan) |

---

## 🛠️ Requirements

- Python 3.8+
- discord.py
- yt-dlp
- ffmpeg

---

## 📦 Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd BotDS
```

### 2. Install Dependencies
```bash
pip install discord.py yt-dlp
```

### 3. Install FFmpeg
**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download dari [ffmpeg.org](https://ffmpeg.org/download.html) atau gunakan:
```bash
choco install ffmpeg
```

---

## ⚙️ Setup

### 1. Buat Discord Bot
1. Buka [Discord Developer Portal](https://discord.com/developers/applications)
2. Klik "New Application"
3. Beri nama bot Anda
4. Buka tab "Bot" dan klik "Add Bot"
5. Copy token bot
6. Di bagian "OAUTH2", centang:
   - `bot` (scopes)
   - `send_messages`, `connect`, `speak` (permissions)

### 2. Setup Token
Edit `bot_new.py` dan ganti token di bagian akhir:
```python
bot.run("YOUR_BOT_TOKEN_HERE")
```

### 3. Setup Cookies (Opsional)
Jika video terlindungi, buat file `cookies.txt` dengan cookies browser Anda.

### 4. Jalankan Bot
```bash
python bot_new.py
```

---

## 🎮 Cara Penggunaan

1. **Invite Bot** - Gunakan invite link dari Discord Developer Portal
2. **Join Voice Channel** - Masuk ke voice channel terlebih dahulu
3. **Gunakan Perintah** - Ketik perintah di text channel
4. **Prefix** - Semua perintah dimulai dengan `!`

### Contoh Sesi
```
!join                     # Bot masuk ke channel
!play despacito           # Putar lagu
!queue                    # Lihat antrian
!play https://youtu.be/... # Putar dari URL
!bassboost 20            # Terapkan bassboost
!shuffle                 # Acak antrian
!skip                    # Skip ke lagu berikutnya
!leave                   # Bot keluar
```

---

## 🔧 Fitur Khusus

### Autoplay
Ketika autoplay diaktifkan, bot akan secara otomatis memutar lagu serupa setelah antrian selesai.

### Loop
Mengulangi lagu yang sedang diputar terus menerus sampai mode loop dimatikan.

### Audio Effects
- **Bassboost**: Meningkatkan bass dengan intensitas (default: 10)
- **Nightcore**: Mempercepat tempo musik hingga 25%

### Auto-Disconnect
Bot akan otomatis meninggalkan voice channel jika:
- Tidak ada lagu yang diputar
- Hanya bot yang ada di channel
- Sudah idle selama 5 menit

---

## 📝 Struktur File

```
BotDS/
├── bot_new.py          # Main bot file
├── cookies.txt         # Cookies untuk authenticated requests (opsional)
└── README.md          # Dokumentasi
```

---

## ⚠️ Tips & Troubleshooting

### Bot tidak bisa terhubung ke voice
- Pastikan bot memiliki permission `Connect` dan `Speak`
- Pastikan FFmpeg ter-install dengan benar

### Lagu tidak bisa diputar
- Periksa koneksi internet
- Coba gunakan URL YouTube langsung
- Update yt-dlp: `pip install --upgrade yt-dlp`

### Audio output tidak terdengar
- Periksa permission `Speak` di channel
- Atur volume dengan `!volume 100`

---

## 🚀 Update & Maintenance

Untuk update yt-dlp (penting untuk kompatibilitas YouTube):
```bash
pip install --upgrade yt-dlp
```

---

## 📄 Lisensi

Dibuat oleh NOEKZ
Remake oleh HAMDAN

---

## 🤝 Support

Jika ada pertanyaan atau issue, silakan buat issue di repository atau hubungi pembuat bot.

---

**Happy Music! 🎵**
