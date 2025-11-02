# 📁 LOYIHA STRUKTURASI

```
updated_library_bot/
│
├── 📄 README.md                      # To'liq yo'riqnoma
├── 📄 INSTALLATION_GUIDE.md          # Qisqacha ishga tushirish
├── 📄 CHANGELOG.md                   # O'zgarishlar tarixi
├── 📄 PROJECT_STRUCTURE.md           # Bu fayl
│
├── 📄 .env.example                   # Environment variables namunasi
├── 📄 .gitignore                     # Git ignore qoidalari
├── 📄 requirements.txt               # Python dependencies
├── 📄 config.py                      # Asosiy konfiguratsiya
├── 📄 init_database.py               # Database yaratish scripti
│
├── 📁 bot/                           # Bot package
│   ├── 📄 __init__.py
│   ├── 📄 main.py                    # Asosiy bot fayli
│   │
│   ├── 📁 handlers/                  # Command handlerlar
│   │   ├── 📄 __init__.py
│   │   ├── 📄 registration.py       # Ro'yxatdan o'tish
│   │   ├── 📄 subscription.py       # Obuna tizimi
│   │   └── 📄 admin.py               # Admin panel
│   │
│   └── 📁 utils/                     # Yordamchi modullar
│       ├── 📄 __init__.py
│       └── 📄 notification.py        # Bildirishnomalar
│
└── 📁 database/                      # Database package
    ├── 📄 __init__.py
    ├── 📄 models.py                  # Database modellari
    ├── 📄 db_manager.py              # User boshqaruvi
    └── 📄 admin_manager.py           # Admin boshqaruvi
```

## 📝 FAYL TAVSIFLARI

### 📄 Konfiguratsiya Fayllari

#### `.env` (yaratilishi kerak)
```env
BOT_TOKEN=your_bot_token_here
SUPER_ADMIN_ID=your_telegram_id_here
```

#### `config.py`
- Bot sozlamalari
- Tarif rejalari
- Database URL
- Bildirishnoma sozlamalari
- Library ID formati

#### `requirements.txt`
```
aiogram==3.13.1
python-dotenv==1.0.1
```

### 🤖 Bot Fayllari

#### `bot/main.py`
- Asosiy bot entry point
- Dispatcher sozlash
- Handlerlarni ro'yxatdan o'tkazish
- Super Admin yaratish
- Background tasks ishga tushirish

#### `bot/handlers/registration.py`
- `/start` - Botni boshlash
- `/register` - Yangi ro'yxat
- `/link` - Library ID bog'lash
- `/profile` - Profil ko'rish
- `/help` - Yordam

#### `bot/handlers/subscription.py`
- `/subscription` - Tariflar
- `/mysubscription` - Hozirgi tarif
- Tarif tanlash callback'lari

#### `bot/handlers/admin.py`
- `/admin` - Admin panel
- `/approve` - Tarifni tasdiqlash
- `/search` - Qidirish
- `/addadmin` - Admin qo'shish (Super Admin)
- `/removeadmin` - Admin o'chirish (Super Admin)

#### `bot/utils/notification.py`
- `send_expiry_warnings()` - Obuna tugash ogohlantirishlari
- `check_expired_subscriptions()` - Muddati o'tgan obunalarni tekshirish
- `send_notification_to_user()` - Foydalanuvchiga xabar yuborish
- `send_notification_to_admins()` - Adminlarga xabar yuborish

### 🗄️ Database Fayllari

#### `database/models.py`
SQLAlchemy ORM modellari:
- `User` - Foydalanuvchilar
- `Admin` - Adminlar
- `Notification` - Bildirishnomalar

#### `database/db_manager.py`
User boshqaruvi:
- `create_user()` - Yangi foydalanuvchi
- `get_user_by_library_id()` - ID bo'yicha topish
- `get_user_by_telegram_id()` - Telegram ID bo'yicha
- `link_telegram_account()` - Telegram bog'lash
- `update_subscription()` - Obuna yangilash
- `get_statistics()` - Statistika
- `search_users()` - Qidirish

#### `database/admin_manager.py`
Admin boshqaruvi:
- `add_super_admin()` - Super Admin qo'shish
- `add_admin()` - Admin qo'shish
- `remove_admin()` - Admin o'chirish
- `is_admin()` - Admin ekanligini tekshirish
- `is_super_admin()` - Super Admin ekanligini tekshirish
- `get_all_admins()` - Barcha adminlar

### 📚 Dokumentatsiya Fayllari

#### `README.md`
- Loyiha tavsifi
- To'liq o'rnatish yo'riqnomasi
- Buyruqlar ro'yxati
- Database strukturasi
- Debugging qo'llanma
- FAQ

#### `INSTALLATION_GUIDE.md`
- 5 daqiqada ishga tushirish
- Qisqacha qadamlar
- Tezkor muammolarni hal qilish

#### `CHANGELOG.md`
- Versiya tarixi
- Yangi imkoniyatlar
- Tuzatilgan xatolar
- Keyingi rejalar

#### `PROJECT_STRUCTURE.md`
- Bu fayl
- Loyiha strukturasi
- Fayl tavsiflari

### 🔧 Utility Fayllari

#### `init_database.py`
Database yaratish scripti:
```bash
python init_database.py        # Yaratish
python init_database.py --info # Ma'lumot
python init_database.py --help # Yordam
```

#### `.gitignore`
Git ignore qoidalari:
- Python cache
- Virtual environment
- .env fayli
- Database fayllari
- Logs

## 🗄️ DATABASE STRUKTURASI

### `users` jadvali
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    library_id TEXT UNIQUE NOT NULL,      -- ID0001, ID0002...
    telegram_id INTEGER UNIQUE,           -- nullable
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    birth_year INTEGER NOT NULL,
    study_place TEXT NOT NULL,
    subscription_plan TEXT DEFAULT 'Free',
    subscription_end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `admins` jadvali
```sql
CREATE TABLE admins (
    admin_id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    library_id TEXT UNIQUE NOT NULL,      -- userga bog'langan
    full_name TEXT NOT NULL,
    is_super_admin BOOLEAN DEFAULT 0,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by INTEGER,                     -- qaysi admin qo'shgan
    is_active BOOLEAN DEFAULT 1
);
```

## 🔄 DATA FLOW

### Ro'yxatdan o'tish:
```
User → /register
     → FSM (first_name, last_name, phone, birth_year, study_place)
     → DatabaseManager.create_user()
     → Library ID generated (ID0001)
     → Telegram ID linked (optional)
     → Confirmation message
```

### Library ID bog'lash:
```
User → /link
     → FSM (library_id)
     → DatabaseManager.get_user_by_library_id()
     → Phone verification
     → DatabaseManager.link_telegram_account()
     → Success message
```

### Admin qo'shish:
```
Super Admin → /addadmin ID0001
           → DatabaseManager.get_user_by_library_id()
           → AdminManager.add_admin()
           → Notification to new admin
           → Success message
```

### Obuna tasdiqlash:
```
Admin → /approve ID0001 Money
     → DatabaseManager.get_user_by_library_id()
     → DatabaseManager.update_subscription()
     → Notification to user
     → Success message
```

## 🚀 ISHGA TUSHIRISH KETMA-KETLIGI

1. **Dependencies o'rnatish:**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

2. **.env yaratish:**
   ```bash
   cp .env.example .env
   nano .env
   ```

3. **Database yaratish (optional):**
   ```bash
   python init_database.py
   ```

4. **Botni ishga tushirish:**
   ```bash
   python bot/main.py
   ```

5. **Super Admin avtomatik yaratiladi** (.env dagi SUPER_ADMIN_ID dan)

## 📊 MONITORING

### Loglar:
- Terminaldagi real-time loglar
- Log level: INFO
- Format: timestamp - name - level - message

### Database:
```bash
# Statistika
python init_database.py --info

# Yoki bot ichidan
/admin → Statistika
```

### Backup:
```bash
# Manual backup
cp library.db backups/library_$(date +%Y%m%d).db

# Cron job (har kuni)
0 0 * * * cp /path/to/library.db /path/to/backups/library_$(date +\%Y\%m\%d).db
```

## 🔐 XAVFSIZLIK

### Environment Variables:
- `.env` faylni hech qachon GitHub ga yuklaMang
- `.gitignore` da .env bo'lishiga ishonch hosil qiling

### Database:
- SQLite local filesystem da
- Kunlik backup
- Sensitive data uchun encryption (agar kerak bo'lsa)

### Bot Token:
- Tokenni kodga yozmang
- Faqat .env da saqlang
- Agar oshkor bo'lsa, @BotFather dan yangilab oling

---

**Oxirgi yangilanish:** 2025-10-14
**Versiya:** 2.0.0
