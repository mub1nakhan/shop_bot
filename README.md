# Jalyuzi/Parda — Telegram katalog boti

Django (ORM + Admin) + Aiogram 3 (bot) asosidagi mahsulot katalogi boti.
Frontend/web sahifa yo'q — mijoz bilan yagona interfeys Telegram bot.

## Texnologiyalar
- Python 3.12+
- Django 5 (faqat ORM + `/admin/` panel uchun)
- Aiogram 3 (long polling)
- PostgreSQL
- Pillow (rasm maydonlari uchun)

## Loyihaning tuzilishi

```
config/            Django sozlamalari (settings, urls)
catalog/           Category, Product, ProductImage modellari + Admin
bot_users/         TelegramUser, Lead, BotSettings modellari + Admin
bot/               Aiogram bot (handlers, keyboards, services, middlewares)
  handlers/        Telegram update'larni qabul qiluvchi routerlar
  keyboards/       Inline klaviatura builderlar + CallbackData factory'lar
  services/        ORM bilan ishlaydigan yagona qatlam (sync_to_async)
  middlewares/     Foydalanuvchini avtomatik saqlash, throttling
  management/commands/runbot.py   `python manage.py runbot`
media/             Yuklangan rasmlar (kategoriya/mahsulot)
```

## O'rnatish

1. Virtual muhit va kutubxonalar:
```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. `.env` faylini yarating (`.env.example` asosida):
```bash
cp .env.example .env
```
va quyidagilarni to'ldiring:
- `BOT_TOKEN` — @BotFather'dan olingan token
- `POSTGRES_*` — PostgreSQL ma'lumotlari
- `ADMIN_IDS` — bot administratorlarining Telegram ID'lari (vergul bilan)

3. PostgreSQL bazasini yarating:
```bash
createdb blinds_bot
```

4. Migratsiyalarni qo'llash:
```bash
python manage.py migrate
```

5. Admin foydalanuvchi yaratish (Django Admin uchun):
```bash
python manage.py createsuperuser
```

## Ishga tushirish

**Django Admin** (kategoriya/mahsulot qo'shish uchun):
```bash
python manage.py runserver
# http://127.0.0.1:8000/admin/
```

**Telegram bot** (alohida terminalda):
```bash
python manage.py runbot
```

Ikkalasi ham bir xil PostgreSQL bazasidan foydalanadi — Adminda qo'shilgan
har qanday kategoriya/mahsulot botda **kodni o'zgartirmasdan, avtomatik** paydo bo'ladi.

## Admin orqali boshqarish

1. **Kategoriya** qo'shish: Admin → Kategoriyalar → "Qo'shish". `Ota kategoriya`
   maydonini bo'sh qoldirsangiz — asosiy (root) kategoriya, tanlasangiz — sub-kategoriya bo'ladi.
2. **Mahsulot** qo'shish: Admin → Mahsulotlar → "Qo'shish". Kategoriya (afzalan
   sub-kategoriya), nom, narx, qisqacha tavsif kiritiladi; pastda rasm(lar)
   qo'shiladi (bir nechta rasm mumkin, "Asosiy rasm" belgisi bot kartochkasida
   ko'rsatiladigan rasmni belgilaydi).
3. **Bot matnlarini** o'zgartirish: Admin → Bot sozlamalari (salomlashuv matni,
   aloqa telefoni, manzil).
4. **Buyurtmalar**: mijoz mahsulot sahifasida "📞 Buyurtma berish" tugmasini
   bosib raqamini qoldirsa, u Admin → Buyurtmalar / So'rovlar bo'limida ko'rinadi.

## Bot oqimi (flow)

```
/start → Bosh menyu (kategoriyalar)
   → Kategoriya tanlash → Sub-kategoriyalar (agar mavjud bo'lsa)
      → Sub-kategoriya tanlash → Mahsulotlar ro'yxati (sahifalangan)
         → Mahsulot tanlash → Mahsulot kartochkasi (rasm, nom, narx, tavsif)
            → ⬅️ Orqaga | 🏠 Bosh menyu | 📞 Buyurtma berish
```

Agar kategoriyada sub-kategoriya bo'lmasa, u avtomatik "leaf" (oxirgi bosqich)
sifatida ishlaydi va to'g'ridan-to'g'ri mahsulotlar ro'yxatini ko'rsatadi —
ya'ni 1 yoki 2 bosqichli kategoriya tuzilmasi ham qo'llab-quvvatlanadi.

## Production uchun tavsiyalar

- `runbot`ni systemd service yoki `supervisor` orqali doimiy ishlaydigan qilib sozlang.
- `DEBUG=False` va `DJANGO_ALLOWED_HOSTS` to'g'ri domenni ko'rsatishi kerak.
- Media fayllarni (`MEDIA_ROOT`) nginx orqali serve qiling, `DEBUG=False` bo'lganda
  Django o'zi media fayllarni bermaydi.
- Katta rasm hajmlari uchun `Pillow` orqali `ImageField` validatsiyasini kuchaytirish tavsiya etiladi.