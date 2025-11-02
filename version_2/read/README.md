# 📚 KUTUBXONA BOSHQARUV BOT

Telegram bot kutubxona a'zolarini boshqarish va obuna tizimi uchun.

## ✨ ASOSIY IMKONIYATLAR

### 👥 Foydalanuvchilar uchun:
- ✅ Telegram orqali ro'yxatdan o'tish
- ✅ Mavjud Library ID ni bog'lash
- ✅ Tariflarni ko'rish va tanlash
- ✅ Profil ma'lumotlarini ko'rish
- ✅ Obuna muddatini kuzatish

### 👨‍💼 Adminlar uchun:
- ✅ Foydalanuvchilar statistikasi
- ✅ Tariflarni tasdiqlash
- ✅ Foydalanuvchilarni qidirish
- ✅ Obunalarni boshqarish

### ⭐ Super Admin uchun:
- ✅ Yangi adminlar qo'shish
- ✅ Adminlarni o'chirish
- ✅ Adminlar ro'yxati
- ✅ To'liq tizim nazorati

## 🔧 O'RNATISH

### 1. Talablar:
```bash
- Python 3.9+
- pip package manager
- Telegram Bot Token (@BotFather dan)
```

### 2. Loyihani yuklab olish:
```bash
# Git orqali (agar GitHub da bo'lsa)
git clone https://github.com/username/library-bot.git
cd library-bot

# Yoki ZIP faylni ochish
unzip library-bot.zip
cd library-bot
```

### 3. Dependencies o'rnatish:
```bash
# Oddiy usul
pip install -r requirements.txt --break-system-packages

# Yoki virtual environment bilan (tavsiya etiladi)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 4. Environment sozlash:
```bash
# .env.example dan .env fayl yaratish
cp .env.example .env

# .env faylni tahrirlash
nano .env  # yoki istalgan text editor
```

.env fayldagi qiymatlarni to'ldiring:
```env
BOT_TOKEN=sizning_bot_tokeningiz
SUPER_ADMIN_ID=sizning_telegram_id_ingiz
```

**Telegram ID ni bilish uchun:**
- @userinfobot ga /start yuboring
- Yoki @getmyid_bot dan foydalaning

### 5. Botni ishga tushirish:
```bash
python bot/main.py
```

Agar hammasi to'g'ri bo'lsa, quyidagi xabarlarni ko'rasiz:
```
==================================================
📚 KUTUBXONA BOT
==================================================
🤖 Bot ishga tushirilmoqda...
==================================================
🚀 Bot ishga tushmoqda...
✅ Super Admin mavjud: [Ism] (ID0000)
✅ Bot muvaffaqiyatli ishga tushdi!
📡 Polling boshlanmoqda...
```

## 📖 FOYDALANISH YO'RIQNOMASI

### FOYDALANUVCHILAR UCHUN:

#### 1. Ro'yxatdan o'tish:
```
/start - Botni boshlash
/register - Yangi ro'yxat (agar ID yo'q bo'lsa)
```

Keyin quyidagi ma'lumotlarni kiriting:
- Ism
- Familiya
- Telefon raqam
- Tug'ilgan yil
- O'quv joyi

#### 2. Library ID ni bog'lash:
Agar allaqachon Library ID bor bo'lsa:
```
/link - Library ID ni bog'lash
```

Keyin:
- Library ID ni kiriting (ID0001)
- Telefon raqamni tasdiqlang

#### 3. Boshqa buyruqlar:
```
/subscription - Tariflarni ko'rish/tanlash
/profile - Profil ma'lumotlari
/help - Yordam
```

### ADMINLAR UCHUN:

#### 1. Admin panel:
```
/admin - Admin panelga kirish
```

#### 2. Statistika:
Admin panelda "📊 Statistika" tugmasini bosing

#### 3. Foydalanuvchilarni ko'rish:
Admin panelda "👥 Foydalanuvchilar" tugmasini bosing

#### 4. Tarifni tasdiqlash:
```
/approve ID0001 Money
/approve ID0001 Premium
/approve ID0001 Free
```

#### 5. Qidirish:
```
/search Abdulloh
/search ID0001
/search +998901234567
```

### SUPER ADMIN UCHUN:

#### 1. Yangi admin qo'shish:
```
/addadmin ID0001
```

**Muhim:** Faqat ro'yxatdan o'tgan va Telegram bog'langan foydalanuvchilarni admin qilish mumkin!

#### 2. Admin o'chirish:
```
/removeadmin ID0001
```

#### 3. Adminlar ro'yxati:
Admin panelda "👨‍💼 Adminlar" tugmasini bosing

## 📁 LOYIHA STRUKTURASI

```
updated_library_bot/
├── bot/
│   ├── main.py                    # Asosiy bot fayli
│   ├── handlers/
│   │   ├── registration.py       # Ro'yxatdan o'tish
│   │   ├── subscription.py       # Obuna tizimi
│   │   └── admin.py               # Admin panel
│   └── utils/
│       └── notification.py        # Bildirishnomalar
├── database/
│   ├── models.py                  # Database modellari
│   ├── db_manager.py              # User boshqaruvi
│   └── admin_manager.py           # Admin boshqaruvi
├── config.py                      # Konfiguratsiya
├── requirements.txt               # Dependencies
├── .env.example                   # Environment namunasi
└── README.md                      # Bu fayl
```

## 🗄️ DATABASE STRUKTURA

### Users jadvali:
- `id` - Auto increment ID
- `library_id` - Asosiy identifikator (ID0001, ID0002...)
- `telegram_id` - Telegram ID (nullable)
- `first_name` - Ism
- `last_name` - Familiya
- `phone_number` - Telefon
- `birth_year` - Tug'ilgan yil
- `study_place` - O'quv joyi
- `subscription_plan` - Tarif (Free, Money, Premium)
- `subscription_end_date` - Obuna tugash sanasi
- `is_active` - Faol/Nofaol
- `created_at` - Ro'yxatdan o'tgan sana

### Admins jadvali:
- `admin_id` - Auto increment ID
- `telegram_id` - Telegram ID (majburiy)
- `library_id` - Library ID (userga bog'langan)
- `full_name` - To'liq ism
- `is_super_admin` - Super admin yoki yo'q
- `added_date` - Qo'shilgan sana
- `added_by` - Qaysi admin qo'shgan
- `is_active` - Faol/Nofaol

## ⚙️ KONFIGURATSIYA

`config.py` faylida quyidagilarni sozlash mumkin:

### Tariflar:
```python
SUBSCRIPTION_PLANS = {
    'Free': {
        'price': 0,
        'duration_days': 0,
        'features': [...]
    },
    'Money': {
        'price': 50000,  # So'm
        'duration_days': 30,
        'features': [...]
    },
    'Premium': {
        'price': 100000,
        'duration_days': 30,
        'features': [...]
    }
}
```

### Bildirishnomalar:
```python
WARNING_DAYS = 3  # Necha kun qolganida ogohlantirish
CHECK_INTERVAL_HOURS = 6  # Har necha soatda tekshirish
```

## 🔄 BOTNI AVTOMATIK ISHGA TUSHIRISH

### Linux/Mac (systemd):
1. Service fayl yaratish:
```bash
sudo nano /etc/systemd/system/library-bot.service
```

2. Quyidagini yozing:
```ini
[Unit]
Description=Library Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/library-bot
ExecStart=/usr/bin/python3 /path/to/library-bot/bot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Ishga tushirish:
```bash
sudo systemctl enable library-bot
sudo systemctl start library-bot
sudo systemctl status library-bot
```

### Windows (Task Scheduler):
1. Task Scheduler ni oching
2. Create Basic Task
3. Python va bot/main.py yo'lini kiriting
4. At startup yoki At log on tanlang

## 🐛 DEBUGGING

### Loglarni ko'rish:
Botni terminalda ishga tushirsangiz, barcha loglar ko'rinadi:
```bash
python bot/main.py
```

### Keng log uchun:
`bot/main.py` da LOG_LEVEL ni o'zgartiring:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Umumiy xatolar:

**1. Bot token xato:**
```
.env faylda BOT_TOKEN ni tekshiring
```

**2. Database xatosi:**
```
library.db faylni o'chirib, qaytadan yarating
```

**3. Import xatolari:**
```
pip install -r requirements.txt --break-system-packages
```

## 📊 MONITORING

### Statistika:
- Admin panel orqali `/admin` → "📊 Statistika"
- Jami foydalanuvchilar
- Tarif bo'yicha taqsimlash
- Adminlar soni

### Database backup:
```bash
# Kunlik backup
cp library.db library_backup_$(date +%Y%m%d).db

# Yoki cron job
0 0 * * * cp /path/to/library.db /path/to/backups/library_$(date +\%Y\%m\%d).db
```

## 🔒 XAVFSIZLIK

1. **Environment variables:**
   - .env faylni hech qachon GitHub ga yuklaMang!
   - .gitignore da .env bo'lishiga ishonch hosil qiling

2. **Database:**
   - Kunlik backup oling
   - Maxfiy ma'lumotlarni shifrlang (agar kerak bo'lsa)

3. **Bot token:**
   - Tokenni hech qachon kodga yozmang
   - Agar token oshkor bo'lsa, @BotFather dan yangilab oling

## 🆘 YORDAM

### Savollar:
- Telegram: @your_support_username
- Email: support@example.com

### Issues:
GitHub Issues bo'limida xato/takliflaringizni yuboring

## 📝 LITSENZIYA

MIT License - batafsil LICENSE faylida

## 🤝 HISSA QO'SHISH

Pull requestlar qabul qilinadi!

1. Fork qiling
2. Yangi branch yarating (`git checkout -b feature/AmazingFeature`)
3. Commit qiling (`git commit -m 'Add some AmazingFeature'`)
4. Push qiling (`git push origin feature/AmazingFeature`)
5. Pull Request oching

## 📌 VERSIYA

**v2.0.0** - Yangilangan versiya
- ✅ Library ID asosiy identifikator
- ✅ Telegram ID ixtiyoriy
- ✅ Ko'p adminlar tizimi
- ✅ Super admin paneli
- ✅ Library ID ni bog'lash imkoniyati

---

**Yaratuvchi:** Your Name
**Sana:** 2025
**Telegram:** @your_username
