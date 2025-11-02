# 🚀 TEZKOR ISHGA TUSHIRISH YO'RIQNOMASI

## ⚡ 5 DAQIQADA ISHGA TUSHIRISH

### 1️⃣ Bot Token olish (2 daqiqa)

1. Telegram da @BotFather ni oching
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: My Library Bot)
4. Bot username ini kiriting (masalan: mylibrarybot)
5. Token ni nusxalab oling (masalan: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2️⃣ Telegram ID ni bilish (1 daqiqa)

1. @userinfobot ni oching
2. `/start` yuboring
3. ID ni nusxalab oling (masalan: `123456789`)

### 3️⃣ Loyihani sozlash (2 daqiqa)

```bash
# 1. Dependencies o'rnatish
pip install aiogram python-dotenv --break-system-packages

# 2. .env fayl yaratish
cp .env.example .env

# 3. .env faylni tahrirlash
nano .env
```

`.env` faylga quyidagilarni kiriting:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
SUPER_ADMIN_ID=123456789
```

**DIQQAT:** O'zingizning real token va ID larni kiriting!

### 4️⃣ Botni ishga tushirish (10 soniya)

```bash
python bot/main.py
```

### 5️⃣ Botni sinab ko'rish

1. Telegram da o'z botingizni oching
2. `/start` yuboring
3. `/admin` buyrug'ini sinab ko'ring (siz Super Admin bo'lganingiz uchun ishlaishi kerak)

## ✅ MUVAFFAQIYATLI!

Agar quyidagicha xabarlar ko'rsangiz, hammasi to'g'ri:
```
✅ Super Admin mavjud: [Ismingiz] (ID0000)
✅ Bot muvaffaqiyatli ishga tushdi!
```

---

## 📱 KEYINGI QADAMLAR

### Birinchi foydalanuvchini ro'yxatdan o'tkazish:

1. Telegram da botingizga `/start` yuboring
2. `/register` ni bosing
3. Barcha ma'lumotlarni kiriting

### Admin qo'shish:

1. Biror foydalanuvchini ro'yxatdan o'tkazing
2. `/admin` buyrug'i orqali Admin panelga kiring
3. "➕ Admin qo'shish" tugmasini bosing
4. `/addadmin ID0001` formatida buyruq yuboring

### Tariflarni sozlash:

`config.py` faylini oching va `SUBSCRIPTION_PLANS` ni o'zgarting:

```python
SUBSCRIPTION_PLANS = {
    'Money': {
        'price': 50000,  # So'mda
        'duration_days': 30,
        ...
    }
}
```

---

## ❓ MUAMMOLAR

### Bot ishga tushmayapti?

**1. Token xato:**
```bash
# .env faylni tekshiring
cat .env
```

**2. Module topilmayapti:**
```bash
pip install aiogram python-dotenv --break-system-packages
```

**3. Database xatosi:**
```bash
# library.db ni o'chiring va qaytadan ishga tushiring
rm library.db
python bot/main.py
```

### Bot javob bermayapti?

1. Botni to'xtatib, qaytadan ishga tushiring (Ctrl+C, keyin qayta `python bot/main.py`)
2. @BotFather da botingizni `/mybots` → Settings → Group Privacy → Turn off qiling
3. Internetga ulanishni tekshiring

---

## 📞 YORDAM

Agar muammo yechilmasa:
- README.md faylni o'qing (to'liq yo'riqnoma)
- Telegram: @your_support_username
- GitHub Issues: github.com/username/library-bot/issues

---

## 🎉 QISQACHA BUYRUQLAR

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni boshlash |
| `/register` | Yangi ro'yxat |
| `/link` | Library ID bog'lash |
| `/admin` | Admin panel |
| `/subscription` | Tariflar |
| `/profile` | Profil |

---

**Omad tilaymiz! 🚀**
