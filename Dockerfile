# =====================================================================
# Dockerfile — "web" servisi (Django + Gunicorn) uchun image retsepti.
#
# Image     — dastur ishlashi uchun kerak bo'lgan hamma narsa (Python,
#             paketlar, loyiha kodi) solingan tayyor qolip. O'zgarmaydi.
# Konteyner — shu qolipdan ishga tushirilgan jonli jarayon.
#             Bitta image'dan istalgancha konteyner yaratish mumkin.
#
# Har bir buyruq (FROM, RUN, COPY ...) image'da yangi qatlam (layer)
# yaratadi. Docker qatlamlarni keshlaydi: o'zgarmagan qatlam qayta
# qurilmaydi, shuning uchun buyruqlar tartibi muhim.
#
# Qo'lda build qilish (odatda compose o'zi qiladi):
#   docker build -t lms-web .
# =====================================================================


# Asos image — Docker Hub'dagi rasmiy Python 3.14.
# "slim" — keraksiz tizim paketlari olib tashlangan yengil varianti.
# Lokal kompyuterdagi Python versiyasi bilan bir xil bo'lgani yaxshi.
FROM python:3.14-slim


# Muhit o'zgaruvchilari (konteyner ichida doim o'rnatilgan bo'ladi):
#   PYTHONDONTWRITEBYTECODE=1       — .pyc kesh fayllari yozilmaydi
#   PYTHONUNBUFFERED=1              — print va loglar darhol chiqadi,
#                                     "docker compose logs" da kechikmaydi
#   PIP_NO_CACHE_DIR=1              — pip yuklab olgan arxivlarni saqlamaydi,
#                                     image hajmi kichik bo'ladi
#   PIP_DISABLE_PIP_VERSION_CHECK=1 — pip "yangi versiya chiqdi" deb
#                                     internetni tekshirib o'tirmaydi
#   PIP_ROOT_USER_ACTION=ignore     — "pip root nomidan ishlayapti" degan
#                                     ogohlantirishni o'chiradi. Konteyner
#                                     ichida bu xavfsiz, chunki u alohida muhit
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore


# Konteyner ichidagi ishchi papka. Papka yo'q bo'lsa, yaratiladi.
# Keyingi COPY, RUN, CMD buyruqlari shu papkada bajariladi.
WORKDIR /app


# Avval FAQAT requirements.txt ni ko'chirib, paketlarni o'rnatamiz.
# Sababi — qatlam keshi: loyiha kodi o'zgarsa-yu requirements.txt
# o'zgarmasa, Docker bu ikki qatlamni keshdan oladi va "pip install"
# qayta ishlamaydi. Build bir necha daqiqa emas, bir necha soniya davom etadi.
COPY requirements.txt .
RUN pip install -r requirements.txt


# Endi loyihaning qolgan kodini ko'chiramiz.
# Birinchi nuqta — kompyuterdagi joriy papka, ikkinchisi — konteynerdagi /app.
# .dockerignore faylida yozilganlar (.env, .venv, media ...) ko'chirilmaydi.
COPY . .


# Xavfsizlik: server dasturi root (to'liq huquqli) foydalanuvchi nomidan
# ishlamasligi kerak. Oddiy "app" foydalanuvchisini yaratamiz.
#
# staticfiles va media papkalarini oldindan yaratib, egasini "app" qilamiz.
# Bu papkalarga keyinchalik volume ulanadi. Volume birinchi marta
# ulanganda papka egasi volume'ga ham o'tadi va gunicorn u yerga
# fayl yoza oladi (masalan, foydalanuvchi rasm yuklaganda).
#
# chmod +x entrypoint.sh — skriptni bajariladigan qilib belgilaymiz.
RUN useradd --uid 1000 --create-home app \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R app:app /app/staticfiles /app/media \
    && chmod +x /app/entrypoint.sh


# Shu qatordan keyingi barcha buyruqlar va konteynerning o'zi
# "app" foydalanuvchisi nomidan ishlaydi.
USER app


# Hujjat vazifasini bajaradi: "bu konteyner 8000-portni tinglaydi".
# Portni tashqi dunyoga OCHMAYDI. Tashqariga faqat nginx ochiladi
# (compose.yaml dagi "ports" bo'limi).
EXPOSE 8000


# Konteyner ishga tushganda avval shu skript ishlaydi.
# U migratsiyalarni qo'llaydi, static fayllarni yig'adi va oxirida
# quyidagi CMD buyrug'ini ishga tushiradi. Ichida izohlari bor.
ENTRYPOINT ["/app/entrypoint.sh"]


# ENTRYPOINT skripti oxirida ishga tushiradigan buyruq — Gunicorn.
# runserver faqat dasturlash uchun, production'da Gunicorn ishlatiladi.
#
#   config.wsgi:application  — Django'ning kirish nuqtasi (config/wsgi.py)
#   --bind 0.0.0.0:8000      — konteyner ichidagi barcha manzillarda 8000-port
#                              (127.0.0.1 bo'lsa, nginx konteyneri ulana olmaydi)
#   --workers 2              — parallel ishlaydigan jarayonlar soni. Har biri
#                              ~100 MB RAM oladi: 1 GB server uchun 2, 2 GB uchun 3
#   --timeout 120            — bitta so'rovga 120 soniyagacha vaqt beriladi
#   --max-requests 500       — har bir worker 500 ta so'rovdan keyin yangilanadi,
#   --max-requests-jitter 50   bu xotira asta-sekin to'lib qolishining oldini oladi
#   --access-logfile -       — so'rovlar logi ekranga chiqadi ("-" = stdout)
#   --error-logfile -        — xatolar logi ham ekranga chiqadi
#
# Docker ekranga chiqqan hamma narsani yig'adi:
#   docker compose logs web
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--max-requests", "500", "--max-requests-jitter", "50", "--access-logfile", "-", "--error-logfile", "-"]
