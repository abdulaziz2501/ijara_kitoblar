# 📝 O'ZGARISHLAR TARIXI

## [2.0.0] - 2025-10-14

### ✨ YANGI IMKONIYATLAR

#### 🔑 Library ID Tizimi
- **Library ID asosiy identifikator** sifatida ishlatiladi (ID0001, ID0002...)
- **Telegram ID ixtiyoriy** (nullable) bo'ldi - ba'zi foydalanuvchilar Telegram orqali emas
- Mavjud Library ID ni Telegram akkauntga **bog'lash** imkoniyati (`/link`)
- Har bir foydalanuvchi noyob Library ID oladi

#### 👨‍💼 Ko'p Adminlar Tizimi
- **Super Admin** tizimi qo'shildi
- Bir nechta **oddiy adminlar** qo'shish imkoniyati
- Super Admin boshqa adminlarni qo'shishi va o'chirishi mumkin
- Adminlar database da alohida jadvalda saqlanadi

#### 📱 Ro'yxatdan O'tish
- Ikki xil ro'yxatdan o'tish usuli:
  1. Yangi ro'yxat (`/register`) - Library ID avtomatik beriladi
  2. Mavjud ID ni bog'lash (`/link`) - telefon orqali tasdiqlash

#### 🔐 Xavfsizlik
- Telefon raqam orqali tasdiqlash (Library ID bog'lashda)
- Admin huquqlarini tekshirish
- Super Admin huquqlarini alohida tekshirish

### 🔄 O'ZGARISHLAR

#### Database Strukturasi
- `users` jadvaliga `library_id` asosiy identifikator qo'shildi
- `telegram_id` nullable bo'ldi
- Yangi `admins` jadvali yaratildi
- Index'lar optimallashtirildi

#### Admin Panel
- Super Admin uchun qo'shimcha tugmalar
- Adminlar ro'yxatini ko'rish
- Statistika yangilandi (adminlar soni qo'shildi)

#### Buyruqlar
Yangi buyruqlar:
- `/link` - Library ID bog'lash
- `/addadmin ID0001` - Admin qo'shish (Super Admin)
- `/removeadmin ID0001` - Admin o'chirish (Super Admin)
- `/search [query]` - Foydalanuvchilarni qidirish
- `/cancel` - Jarayonni bekor qilish

O'zgargan buyruqlar:
- `/admin` - Endi Super Admin uchun qo'shimcha imkoniyatlar
- `/approve` - Library ID bilan ishlaydi

### 🐛 TUZATILGAN XATOLAR

- Telegram ID nullable bo'lmasligi muammosi tuzatildi
- Bot ishlamasligi xatosi tuzatildi (Telegram ID yo'q bo'lganda)
- Bildirishnomalar faqat Telegram ID bor foydalanuvchilarga yuboriladi
- Admin tekshirish mantiqiy xatolari tuzatildi

### 📚 Dokumentatsiya

- `README.md` to'liq qayta yozildi
- `INSTALLATION_GUIDE.md` qisqacha yo'riqnoma qo'shildi
- Har bir fayl uchun docstring qo'shildi
- Kodlarga tushuntirish commentlar qo'shildi

### 🔧 Texnik O'zgarishlar

- Logging yaxshilandi
- Error handling kengaytirildi
- Database manager qayta yozildi
- Admin manager yangi modul qo'shildi
- Notification tizimi yangilandi

---

## [1.0.0] - 2024-XX-XX

### Dastlabki Versiya
- Asosiy bot funksiyalari
- Ro'yxatdan o'tish tizimi
- Obuna tizimi
- Oddiy admin panel
- Bildirishnomalar

---

## 📋 Keyingi Rejalar (v2.1.0)

### Rejalashtirilgan:
- [ ] Kitoblar bazasi qo'shish
- [ ] Kitob ijarasi tizimi
- [ ] QR kod orqali Library ID skanerlash
- [ ] Streamlit dashboard
- [ ] To'lov tizimi integratsiyasi (Click, Payme)
- [ ] Statistika export (Excel, PDF)
- [ ] Bot backup tizimi
- [ ] Multi-language support (O'zbek, Rus)

### Ko'rib chiqilmoqda:
- [ ] Telegram mini-app
- [ ] Web admin panel
- [ ] SMS bildirishnomalar
- [ ] Mobil ilova (opsional)

---

## 🤝 Hissa Qo'shish

Agar siz loyihaga hissa qo'shmoqchi bo'lsangiz:
1. Issue oching (muammo/taklif)
2. Fork qiling
3. Pull Request yuboring

---

## 📝 Versiyalash

Bu loyiha [Semantic Versioning](https://semver.org/) dan foydalanadi:
- **MAJOR** - Eski versiya bilan mos kelmaydigan o'zgarishlar
- **MINOR** - Yangi imkoniyatlar (eski versiya bilan mos)
- **PATCH** - Xato tuzatishlar

Masalan: `2.0.0`
- `2` - Major versiya
- `0` - Minor versiya
- `0` - Patch versiya
