# LMS-U12 — Deploy qo'llanmasi

Ubuntu 24.04 + Nginx + Gunicorn + PostgreSQL 16 + Django 6.0

Buyruqlarni **yuqoridan pastga, bittalab** bajaring. Har bir bo'limda buyruq qayerda ishlashi ko'rsatilgan:

- 🖥 **LOKAL** — o'z kompyuteringizda (loyiha papkasida)
- ☁️ **SERVER** — SSH orqali serverda

---

## 0. Ma'lumotlar

Deploy boshlashdan oldin quyidagilarni yozib oling:

| Nima | Bu loyihada |
|---|---|
| Server IP | `51.20.4.14` |
| SSH user | `ubuntu` |
| PEM kalit | `~/Desktop/macos.pem` |
| GitHub repo | `https://github.com/temuralidavron/LMS-U12.git` |
| Loyiha papkasi (server) | `/srv/lms-u12` |
| Baza nomi | `lms_u12` |
| Baza useri | `lms_user` |
| systemd servis | `lms-u12` |

Boshqa serverda ishlatsangiz — shu qiymatlarni almashtiring.

---

## 1. AWS Security Group — portlarni ochish

EC2 Console → **Instances** → instance → **Security** tab → Security Group havolasi → **Edit inbound rules**.

Ikkita qoida bo'lishi shart. **Muhim:** har bir qoida uchun `Add rule` tugmasini bosing — mavjud qatorni tahrirlamang, aks holda eski qoida yo'qoladi.

| Type | Protocol | Port | Source |
|---|---|---|---|
| SSH | TCP | 22 | Anywhere-IPv4 (`0.0.0.0/0`) |
| HTTP | TCP | 80 | Anywhere-IPv4 (`0.0.0.0/0`) |

`Save rules` bosgach, ro'yxatda **Inbound rules (2)** ko'rinishi kerak. Agar `(1)` bo'lsa — qoida qo'shilmagan, tahrirlangan.

---

## 2. 🖥 LOKAL — PEM kalit huquqini to'g'rilash

SSH ochiq huquqli kalitni rad etadi.

```bash
chmod 400 ~/Desktop/macos.pem
```

---

## 3. 🖥 LOKAL — SSH ulanishni tekshirish

```bash
ssh -i ~/Desktop/macos.pem ubuntu@51.20.4.14 'echo SSH ishladi'
```

`SSH ishladi` chiqsa — davom eting. `Operation timed out` chiqsa — 1-bo'limga qayting, 22-port yopiq.

---

## 4. ☁️ SERVER — tizimni tayyorlash

Serverga kiring:

```bash
ssh -i ~/Desktop/macos.pem ubuntu@51.20.4.14
```

### 4.1. Swap qo'shish

1 GB RAM'li serverda `pip install` va `collectstatic` xotira yetmay to'xtashi mumkin. 1 GB swap buni oldini oladi.

```bash
sudo fallocate -l 1G /swapfile
```

```bash
sudo chmod 600 /swapfile
```

```bash
sudo mkswap /swapfile
```

```bash
sudo swapon /swapfile
```

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Tekshirish:

```bash
free -h
```

### 4.2. Paketlarni o'rnatish

```bash
sudo apt-get update
```

```bash
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv python3-pip nginx postgresql postgresql-contrib
```

Tekshirish:

```bash
nginx -v && psql --version && python3 --version
```

Django 6.0 uchun Python **3.12+** kerak. Ubuntu 24.04 da 3.12.3 keladi — mos.

### 4.3. PostgreSQL bazasi va useri

Avval parol generatsiya qilib, faylga saqlaymiz (keyin `.env` ga kerak bo'ladi):

```bash
openssl rand -base64 24 | tr -d '/+=' | head -c 24 > ~/.lms_db_pass && chmod 600 ~/.lms_db_pass && echo && cat ~/.lms_db_pass
```

User yaratish:

```bash
sudo -u postgres psql -c "CREATE USER lms_user WITH PASSWORD '$(cat ~/.lms_db_pass)';"
```

```bash
sudo -u postgres psql -c "ALTER ROLE lms_user SET client_encoding TO 'utf8';"
```

```bash
sudo -u postgres psql -c "ALTER ROLE lms_user SET default_transaction_isolation TO 'read committed';"
```

```bash
sudo -u postgres psql -c "ALTER ROLE lms_user SET timezone TO 'UTC';"
```

```bash
sudo -u postgres psql -c "ALTER USER lms_user CREATEDB;"
```

Baza yaratish:

```bash
sudo -u postgres psql -c "CREATE DATABASE lms_u12 OWNER lms_user ENCODING 'UTF8';"
```

Tekshirish:

```bash
sudo -u postgres psql -l | grep lms_u12
```

---

## 5. 🖥 LOKAL — loyihani prod uchun tayyorlash

> Bu bo'lim LMS-U12 loyihasida **allaqachon bajarilgan**. Yangi loyihada takrorlash uchun saqlangan.

### 5.1. `.gitignore`

```
__pycache__/
*.py[cod]
*.so

.venv/
venv/
env/

.env
*.env
!.env.example

db.sqlite3
db.sqlite3-journal
*.dump
data.json

staticfiles/
media/

.idea/
.vscode/
.DS_Store
*.log
```

### 5.2. `requirements.txt`

```
Django==6.0.7
pillow==12.3.0
psycopg[binary]
gunicorn
python-dotenv
```

`psycopg[binary]` — psycopg3, kompilyatsiya talab qilmaydi (1 GB RAM'da muhim).

### 5.3. `config/settings.py`

Yuqori qismini shunday qiling:

```python
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


def env_bool(name, default='False'):
    return os.environ.get(name, default).strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-development-key-only')

DEBUG = env_bool('DEBUG')

if not DEBUG and SECRET_KEY.startswith('django-insecure-'):
    raise ImproperlyConfigured('SECRET_KEY must be set in .env when DEBUG is off')

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')

CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
```

`DATABASES` blokini almashtiring:

```python
if os.environ.get('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASSWORD'],
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

Mantiq: `DB_NAME` bo'lsa → PostgreSQL, bo'lmasa → SQLite. Ya'ni lokalda hech narsa buzilmaydi.

`STATIC_ROOT` allaqachon bor bo'lishi kerak:

```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### 5.4. Lokal `.env`

`DEBUG` sukut bo'yicha `False` — lokalda ishlashi uchun `.env` kerak. Bu fayl git'ga kirmaydi.

```bash
printf 'DEBUG=True\nSECRET_KEY=django-insecure-local-only\nALLOWED_HOSTS=localhost,127.0.0.1\n' > .env
```

Tekshirish:

```bash
.venv/bin/pip install python-dotenv
```

```bash
.venv/bin/python manage.py check
```

`System check identified no issues` chiqishi kerak.

### 5.5. Mavjud ma'lumotni eksport qilish

SQLite'dagi ma'lumotni PostgreSQL'ga ko'chirish uchun.

```bash
.venv/bin/python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e sessions --indent 2 -o data.json
```

Tekshirish:

```bash
ls -lh data.json
```

> Yangi loyihada ma'lumot bo'lmasa — bu qadamni va 10-bo'limni o'tkazib yuboring.

### 5.6. Git'ga push

`.gitignore` ni eski, allaqachon kuzatilayotgan fayllarga ham qo'llash uchun index'ni qayta yig'amiz. Bu **fayllarni diskdan o'chirmaydi**, faqat git kuzatuvidan chiqaradi.

```bash
git rm -r --cached . -q
```

```bash
git add .
```

```bash
git status --short
```

Natijada `.pyc`, `db.sqlite3`, `.idea/`, `media/` — `D` belgisi bilan chiqadi. Shundan keyin:

```bash
git commit -m "Production konfiguratsiya: env-based settings, requirements, gitignore"
```

```bash
git push
```

---

## 6. ☁️ SERVER — kodni klonlash

```bash
sudo mkdir -p /srv/lms-u12
```

```bash
sudo chown ubuntu:ubuntu /srv/lms-u12
```

```bash
sudo chmod 755 /srv/lms-u12
```

```bash
git clone https://github.com/temuralidavron/LMS-U12.git /srv/lms-u12
```

> Repo private bo'lsa: GitHub'da **Deploy key** yarating (`ssh-keygen -t ed25519 -f ~/.ssh/deploy_key` → public kalitni repo Settings → Deploy keys ga qo'shing) va SSH URL bilan klonlang.

---

## 7. ☁️ SERVER — virtual muhit va paketlar

```bash
cd /srv/lms-u12
```

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install --upgrade pip
```

```bash
.venv/bin/pip install -r requirements.txt
```

Tekshirish:

```bash
.venv/bin/pip list
```

---

## 8. ☁️ SERVER — `.env` yaratish

SECRET_KEY generatsiya qilib, `.env` ni to'liq yozamiz:

```bash
cd /srv/lms-u12 && printf 'DEBUG=False\nSECRET_KEY=%s\nALLOWED_HOSTS=51.20.4.14,localhost,127.0.0.1\nCSRF_TRUSTED_ORIGINS=http://51.20.4.14\n\nDB_NAME=lms_u12\nDB_USER=lms_user\nDB_PASSWORD=%s\nDB_HOST=localhost\nDB_PORT=5432\n' "$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')" "$(cat ~/.lms_db_pass)" > .env
```

```bash
chmod 600 /srv/lms-u12/.env
```

Tekshirish (parol ko'rinadi — ekranni boshqa hech kim ko'rmasin):

```bash
cat /srv/lms-u12/.env
```

Django konfiguratsiyani o'qiy olishini tekshirish:

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py check
```

---

## 9. ☁️ SERVER — migratsiyalar

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py migrate
```

Tekshirish:

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py showmigrations
```

Hammasi `[X]` bo'lishi kerak.

---

## 10. ☁️/🖥 Ma'lumotni ko'chirish

### 10.1. 🖥 LOKAL — `data.json` ni yuborish

Yangi terminal oching (serverdan chiqmasdan):

```bash
scp -i ~/Desktop/macos.pem data.json ubuntu@51.20.4.14:/srv/lms-u12/
```

### 10.2. ☁️ SERVER — import qilish

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py loaddata data.json
```

`Installed 81 object(s)` kabi natija chiqadi. Tekshirish:

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py shell -c "from django.contrib.auth import get_user_model; print('Userlar:', get_user_model().objects.count())"
```

Import tugagach `data.json` da parollar hash holida yotadi — o'chirib tashlang:

```bash
rm /srv/lms-u12/data.json
```

---

## 11. 🖥 LOKAL — media fayllarni yuborish

`media/` git'da yo'q, shuning uchun alohida ko'chiriladi.

```bash
scp -i ~/Desktop/macos.pem -r media ubuntu@51.20.4.14:/srv/lms-u12/
```

Tekshirish (☁️ SERVER):

```bash
ls -R /srv/lms-u12/media | head -20
```

---

## 12. ☁️ SERVER — static fayllarni yig'ish

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py collectstatic --noinput
```

Tekshirish:

```bash
ls /srv/lms-u12/staticfiles/
```

---

## 13. ☁️ SERVER — superuser

Ma'lumot import qilingan bo'lsa, eski adminlar allaqachon bor — bu qadam shart emas.

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py createsuperuser
```

`CustomUser` da `role` maydoni bor va sukut bo'yicha `student` bo'ladi. Superuser uchun `is_admin` property baribir `True` qaytaradi, lekin rolni aniq qo'yish uchun:

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); U.objects.filter(is_superuser=True).update(role='admin'); print('OK')"
```

---

## 14. ☁️ SERVER — Gunicorn (systemd)

Servis faylini yaratish:

```bash
sudo tee /etc/systemd/system/lms-u12.service > /dev/null <<'EOF'
[Unit]
Description=LMS-U12 Gunicorn daemon
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=ubuntu
Group=www-data
WorkingDirectory=/srv/lms-u12
RuntimeDirectory=gunicorn
Environment=PYTHONUNBUFFERED=1
ExecStart=/srv/lms-u12/.venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/gunicorn/lms-u12.sock \
    --umask 007 \
    --timeout 120 \
    --max-requests 500 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

Sozlamalar izohi:
- `--workers 3` — 2 vCPU / 1 GB RAM uchun. Har bir worker ~100 MB yeydi
- `--timeout 120` — katta video yuklash uchun
- `--max-requests 500` — xotira sizib chiqishini oldini oladi, worker vaqti-vaqti bilan qayta tug'iladi
- `Group=www-data` + `--umask 007` — nginx socket'ga ula olishi uchun

Ishga tushirish:

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl enable --now lms-u12
```

Tekshirish:

```bash
sudo systemctl status lms-u12 --no-pager
```

`active (running)` bo'lishi kerak. Socket joyidami:

```bash
ls -l /run/gunicorn/lms-u12.sock
```

---

## 15. ☁️ SERVER — Nginx

Konfiguratsiya:

```bash
sudo tee /etc/nginx/sites-available/lms-u12 > /dev/null <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name 51.20.4.14 _;

    client_max_body_size 200M;

    location /static/ {
        alias /srv/lms-u12/staticfiles/;
        access_log off;
        expires 30d;
    }

    location /media/ {
        alias /srv/lms-u12/media/;
        access_log off;
        expires 7d;
    }

    location / {
        proxy_pass http://unix:/run/gunicorn/lms-u12.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_redirect off;
    }
}
EOF
```

`client_max_body_size 200M` — dars videolari to'g'ridan-to'g'ri yuklanadi (`FileField`), shuning uchun katta limit.

Standart saytni o'chirib, yangisini yoqish:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

```bash
sudo ln -sf /etc/nginx/sites-available/lms-u12 /etc/nginx/sites-enabled/lms-u12
```

Sintaksisni tekshirish:

```bash
sudo nginx -t
```

**Qayta yuklash — bu qadamsiz eski konfig ishlayveradi:**

```bash
sudo systemctl reload nginx
```

> `reload` darhol tugamaydi — eski worker'lar bir necha soniya eski konfig bilan javob berib turadi. Shu payt test qilsangiz `404` chiqishi mumkin. 2-3 soniya kutib, keyin 16-bo'limga o'ting.

---

## 16. Tekshirish

☁️ SERVER — Django prod tekshiruvi:

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py check --deploy
```

> HTTPS yo'qligi sabab `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS` bo'yicha ogohlantirish chiqadi — bu kutilgan holat. Domen va SSL qo'shilgach yo'qoladi.

☁️ SERVER — ichkaridan javob:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1/accounts/login/
```

🖥 LOKAL — tashqaridan javob:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://51.20.4.14/accounts/login/
```

Ikkalasi ham `200` qaytarishi kerak.

Brauzerda oching: **http://51.20.4.14**

---

## 17. Yangilanishlarni chiqarish (redeploy)

Kod o'zgargach, 🖥 LOKAL:

```bash
git push
```

Keyin ☁️ SERVER:

```bash
cd /srv/lms-u12 && git pull
```

```bash
cd /srv/lms-u12 && .venv/bin/pip install -r requirements.txt
```

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py migrate
```

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py collectstatic --noinput
```

```bash
sudo systemctl restart lms-u12
```

Faqat shablon yoki view o'zgargan bo'lsa, oxirgi buyruqning o'zi yetadi.

---

## 18. Muammolarni hal qilish

### Sayt 502 Bad Gateway

Gunicorn ishlamayapti yoki socket yo'q.

```bash
sudo systemctl status lms-u12 --no-pager
```

```bash
sudo journalctl -u lms-u12 -n 50 --no-pager
```

### Sayt 500 Internal Server Error

Django xatosi. Loglar journald'da:

```bash
sudo journalctl -u lms-u12 -n 100 --no-pager
```

Vaqtincha batafsil xato ko'rish uchun `.env` da `DEBUG=True` qilib, servisni restart qiling — **tekshirgach albatta `False` ga qaytaring**.

### `DisallowedHost` xatosi

`.env` dagi `ALLOWED_HOSTS` ga murojaat qilinayotgan domen/IP kiritilmagan.

```bash
grep ALLOWED_HOSTS /srv/lms-u12/.env
```

### Static fayllar (CSS) yuklanmayapti

```bash
ls /srv/lms-u12/staticfiles/
```

Bo'sh bo'lsa — `collectstatic` bajarilmagan (12-bo'lim). Fayllar bor, lekin 403 bo'lsa — huquq muammosi:

```bash
sudo chmod 755 /srv/lms-u12
```

### Media fayllar 404

```bash
ls /srv/lms-u12/media/
```

Bo'sh bo'lsa — 11-bo'limni bajaring.

### Bazaga ulanmayapti

```bash
sudo systemctl status postgresql --no-pager
```

Parolni solishtiring:

```bash
grep DB_PASSWORD /srv/lms-u12/.env && cat ~/.lms_db_pass
```

### `duplicate key value violates unique constraint`

`loaddata` dan keyin PostgreSQL sequence'lari eskirib qolgan (odatda Django o'zi to'g'rilaydi, lekin har ehtimolga):

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py sqlsequencereset accounts courses auth | .venv/bin/python manage.py dbshell
```

### Xotira yetmayapti / jarayon o'ldirilyapti

```bash
free -h
```

```bash
sudo journalctl -k | grep -i "out of memory" | tail
```

Chiqsa — swap qo'shilmagan (4.1) yoki worker soni ko'p. `lms-u12.service` da `--workers 3` ni `2` ga tushiring.

### Nginx o'zgarishlari ta'sir qilmayapti

`reload` bajarilmagan:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## 19. Deploydan keyingi xavfsizlik ishlari

Deploy ishlagach quyidagilarni bajaring.

### 19.1. SSH ni faqat o'z IP'ingizga cheklash

AWS Console → Security Group → Inbound rules → SSH qatorini tahrirlang → Source: **My IP**.

> Internet provayderingiz IP'ni almashtirsa, qayta kirish uchun IP'ni yangilashingiz kerak bo'ladi.

### 19.2. HTTPS

Sayt faqat HTTP orqali ishlayotgan bo'lsa, login parollari tarmoqda **ochiq** ketadi. To'liq ketma-ketlik — **20-bo'lim**.

### 19.3. Baza zaxirasi

Kunlik dump:

```bash
sudo -u postgres pg_dump lms_u12 | gzip > ~/lms_u12_$(date +%F).sql.gz
```

Tiklash:

```bash
gunzip -c ~/lms_u12_2026-08-01.sql.gz | sudo -u postgres psql lms_u12
```

### 19.4. Avtomatik xavfsizlik yangilanishlari

```bash
sudo apt-get install -y unattended-upgrades
```

```bash
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 20. HTTPS o'rnatish (domen bilan)

Bu bo'limni 16-bo'lim (sayt HTTP orqali ishlayapti) tugagach bajaring.

Quyida domen sifatida `lms.example.uz` ishlatilgan — **hamma buyruqda uni o'z domeningizga almashtiring**.

### 20.1. Domen tanlash

Let's Encrypt sertifikatni **faqat domenga** beradi — IP manzilga (`51.20.4.14`) sertifikat olib bo'lmaydi.

Ikki variant:

| Variant | Misol | Izoh |
|---|---|---|
| Apex domen | `example.uz` | Butun domen LMS'ga ketadi |
| Subdomen | `lms.example.uz` | **Tavsiya** — asosiy domen bo'sh qoladi, LMS'ni keyin boshqa serverga ko'chirish oson |

Subdomen uchun alohida narsa sotib olish shart emas — mavjud domeningizning DNS panelida bitta yozuv qo'shasiz, xolos.

### 20.2. DNS — A record qo'shish

Domen registratori panelida (ahost.uz, GoDaddy, Cloudflare, Namecheap va h.k.) **DNS / DNS Management** bo'limiga kiring va yangi yozuv qo'shing:

| Maydon | Subdomen uchun | Apex uchun |
|---|---|---|
| Type | `A` | `A` |
| Name / Host | `lms` | `@` |
| Value / Points to | `51.20.4.14` | `51.20.4.14` |
| TTL | `300` | `300` |

> Cloudflare ishlatsangiz: proxy (to'q sariq bulut) belgisini **o'chiring** (DNS only / kulrang). Yoqiq bo'lsa certbot HTTP-01 tekshiruvidan o'tolmaydi.

DNS tarqalishini kuting (odatda 5–30 daqiqa), keyin 🖥 LOKAL tekshiring:

```bash
dig +short lms.example.uz
```

Natija aynan `51.20.4.14` bo'lishi shart. Bo'sh yoki boshqa IP chiqsa — kuting, hali tarqalmagan. **Bu qadam tugamasdan certbot ishlamaydi.**

### 20.3. AWS Security Group — 443-portni ochish

EC2 Console → Security Group → **Edit inbound rules** → **`Add rule`** (mavjud qatorlarni tahrirlamang):

| Type | Protocol | Port | Source |
|---|---|---|---|
| HTTPS | TCP | 443 | Anywhere-IPv4 (`0.0.0.0/0`) |

Yakunda **Inbound rules (3)** bo'ladi: SSH 22, HTTP 80, HTTPS 443.

> 80-portni **yopmang** — Let's Encrypt sertifikatni yangilashda o'sha portdan foydalanadi.

### 20.4. 🖥 LOKAL — kodni yangilash

`settings.py` da HTTPS bloki `USE_HTTPS` env o'zgaruvchisi orqali yoqiladi:

```python
USE_HTTPS = env_bool('USE_HTTPS')

if USE_HTTPS:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

`SECURE_PROXY_SSL_HEADER` shart: nginx orqasida Django so'rov HTTPS ekanini faqat `X-Forwarded-Proto` sarlavhasidan biladi. Usiz `SECURE_SSL_REDIRECT` cheksiz redirect halqasiga olib keladi.

Kod allaqachon shunday bo'lsa, bu qadamni o'tkazing. Aks holda:

```bash
git add config/settings.py .env.example
```

```bash
git commit -m "HTTPS sozlamalari"
```

```bash
git push
```

☁️ SERVER'da tortib oling:

```bash
cd /srv/lms-u12 && git pull
```

### 20.5. ☁️ SERVER — nginx'da `server_name` ni domenga o'zgartirish

certbot domenga mos `server` blokini topa olishi kerak:

```bash
sudo sed -i 's/^    server_name .*/    server_name lms.example.uz;/' /etc/nginx/sites-available/lms-u12
```

Tekshiring:

```bash
grep server_name /etc/nginx/sites-available/lms-u12
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 20.6. ☁️ SERVER — certbot va sertifikat

```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

```bash
sudo certbot --nginx -d lms.example.uz
```

certbot uchta savol beradi:

1. **Email** — sertifikat tugashidan oldin ogohlantirish keladi, haqiqiy pochta yozing
2. **Terms of Service** — `Y`
3. **HTTP → HTTPS redirect** — **`2` (Redirect)** ni tanlang

Muvaffaqiyatli bo'lsa `Congratulations! You have successfully enabled HTTPS` chiqadi va nginx konfigi avtomatik yangilanadi (`listen 443 ssl`, sertifikat yo'llari, 80 → 443 redirect).

Sertifikatni ko'rish:

```bash
sudo certbot certificates
```

### 20.7. ☁️ SERVER — Django `.env` ni yangilash

```bash
nano /srv/lms-u12/.env
```

Uchta qatorni shunday qiling (domenni almashtiring):

```
ALLOWED_HOSTS=lms.example.uz,51.20.4.14,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://lms.example.uz
USE_HTTPS=True
```

`USE_HTTPS=True` qatori faylda yo'q bo'lsa — qo'shing. Saqlash: `Ctrl+O`, `Enter`, `Ctrl+X`.

```bash
sudo systemctl restart lms-u12
```

### 20.8. Tekshirish

☁️ SERVER — Django prod tekshiruvi:

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py check --deploy
```

Endi `System check identified no issues` chiqishi kerak — 16-bo'limdagi 4 ta ogohlantirish yo'qoladi.

🖥 LOKAL — HTTP avtomatik HTTPS'ga o'tyaptimi:

```bash
curl -sI http://lms.example.uz/ | head -3
```

`301` va `Location: https://...` bo'lishi kerak.

🖥 LOKAL — HTTPS javobi:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://lms.example.uz/accounts/login/
```

`200` bo'lishi kerak.

🖥 LOKAL — sertifikat ma'lumoti:

```bash
echo | openssl s_client -connect lms.example.uz:443 -servername lms.example.uz 2>/dev/null | openssl x509 -noout -issuer -dates
```

Brauzerda oching: **https://lms.example.uz** — qulf belgisi ko'rinishi kerak.

### 20.9. Avtomatik yangilash

Sertifikat 90 kun amal qiladi. certbot uni o'zi yangilaydi — taymer o'rnatish bilan birga yoqiladi:

```bash
systemctl status certbot.timer --no-pager
```

`active (waiting)` bo'lishi kerak. Yangilashni sinab ko'rish (haqiqiy yangilamaydi):

```bash
sudo certbot renew --dry-run
```

`Congratulations, all simulated renewals succeeded` chiqsa — hammasi joyida, boshqa hech narsa qilish shart emas.

### 20.10. HSTS haqida ogohlantirish

`SECURE_HSTS_SECONDS = 31536000` (1 yil) brauzerga "bu domenga faqat HTTPS orqali kir" deb aytadi. Brauzer buni **eslab qoladi** — sertifikat muddati o'tib ketsa yoki HTTPS buzilsa, foydalanuvchi saytga umuman kira olmaydi va uni tezda orqaga qaytarib bo'lmaydi.

Shuning uchun birinchi kunlarda qiymatni kichik qilib sinang. `.env` ga qo'shing:

```
SECURE_HSTS_SECONDS=3600
```

Bir necha kun muammosiz ishlagach, qatorni olib tashlang — sukut bo'yicha 1 yil qo'llanadi.

> `SECURE_HSTS_PRELOAD` ataylab yoqilmagan. Preload ro'yxatiga qo'shilish — qaytarib bo'lmaydigan qadam, faqat domen doim HTTPS'da qolishiga ishonchingiz komil bo'lsa qiling.

---

## Fayllar joylashuvi (server)

| Yo'l | Nima |
|---|---|
| `/srv/lms-u12/` | loyiha kodi |
| `/srv/lms-u12/.env` | maxfiy sozlamalar (600) |
| `/srv/lms-u12/.venv/` | virtual muhit |
| `/srv/lms-u12/staticfiles/` | yig'ilgan static |
| `/srv/lms-u12/media/` | yuklangan fayllar |
| `/etc/systemd/system/lms-u12.service` | gunicorn servisi |
| `/etc/nginx/sites-available/lms-u12` | nginx konfigi |
| `/run/gunicorn/lms-u12.sock` | gunicorn socket |
| `~/.lms_db_pass` | baza paroli (600) |

## Foydali buyruqlar

```bash
sudo systemctl restart lms-u12
```

```bash
sudo journalctl -u lms-u12 -f
```

```bash
sudo tail -f /var/log/nginx/error.log
```

```bash
cd /srv/lms-u12 && .venv/bin/python manage.py shell
```
