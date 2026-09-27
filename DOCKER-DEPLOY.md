# LMS-U12 — Docker bilan deploy qo'llanmasi

Ubuntu 24.04 + Docker + Nginx + Gunicorn + PostgreSQL 18 + Django 6.0

Bu qo'llanma `DEPLOY.md` ning Docker'li variantidir. `DEPLOY.md` da har bir dastur serverga alohida o'rnatiladi, bu yerda esa hammasi konteynerlarda ishlaydi.

Buyruqlarni **yuqoridan pastga, bittalab** bajaring. Har bir bo'limda buyruq qayerda ishlashi ko'rsatilgan:

- 🖥 **LOKAL** — o'z kompyuteringizda (loyiha papkasida)
- ☁️ **SERVER** — SSH orqali serverda

---

## 0. Ma'lumotlar

Deploy boshlashdan oldin quyidagilarni yozib oling. Qo'llanmadagi buyruqlarda shu qiymatlar ishlatilgan.

| Nima | Bu loyihada |
|---|---|
| Server IP (Elastic IP) | `13.60.107.7` |
| SSH user | `ubuntu` |
| PEM kalit | `~/Downloads/django-key.pem` |
| GitHub repo | `https://github.com/temuralidavron/LMS-U12.git` |
| Loyiha papkasi (server) | `/srv/lms-u12` |
| Compose loyiha nomi | `lms-u12` |
| Baza nomi | `test_db` |
| Baza useri | `test_db_user` |
| Domen | `<DOMEN>` |
| Let's Encrypt email | `<EMAIL>` |

Boshqa serverda ishlatsangiz — shu qiymatlarni almashtiring.

## Umumiy ketma-ketlik

| № | Qadam | Kim |
|---|---|---|
| 1 | Docker nima — tushunchalar | — |
| 2 | Loyihadagi Docker fayllari | — |
| 3 | Lokal kompyuterda sinab ko'rish | 🖥 lokal |
| 4 | AWS: EC2 instance, Security Group, Elastic IP | siz (AWS Console) |
| 5 | SSH, swap, Docker o'rnatish | ☁️ server |
| 6 | Kodni klonlash va `.env` yaratish | ☁️ server |
| 7 | DNS: A record | siz (DNS panel) |
| 8 | 1-bosqich: saytni HTTP orqali ko'tarish | ☁️ server |
| 9 | Ma'lumot va media fayllarni ko'chirish | 🖥 → ☁️ |
| 10 | 2-bosqich: HTTPS sertifikat | ☁️ server |
| 11 | Sertifikatni avtomatik yangilash | ☁️ server |
| 12 | Yangilanish chiqarish (redeploy) | ☁️ server |
| 13 | Zaxira nusxa va tiklash | ☁️ server |
| 14 | Muammolarni hal qilish | — |
| 15 | Xavfsizlik | — |
| 16 | Foydali buyruqlar | — |

8-bo'lim tugaganda sayt IP orqali ishlaydi. 10-bo'lim — domen va HTTPS.

---

## 1. Docker nima va nega kerak

### 1.1. Muammo

`DEPLOY.md` usulida serverga Python, PostgreSQL, Nginx, virtual muhit — hammasi alohida o'rnatiladi. Uchta odatiy muammo shundan chiqadi:

1. **"Mening kompyuterimda ishlayapti"** — serverdagi Python versiyasi boshqacha, paket versiyasi boshqacha va kod boshqacha ishlaydi.
2. **Qo'lda bajarilgan qadamlar** — o'nlab buyruq. Bittasi tushib qolsa, muammoni topish qiyin.
3. **Serverni tozalash qiyin** — o'rnatilgan dasturlar tizimga tarqalib ketadi.

### 1.2. Yechim

Docker dasturni **o'z muhiti bilan birga** o'raydi: kerakli Python versiyasi, paketlar, kod — hammasi bitta "qutida". Qutini istalgan serverga olib borib ishga tushirsangiz, u bir xil ishlaydi.

### 1.3. Asosiy tushunchalar

| Tushuncha | Ma'nosi | Loyihamizda |
|---|---|---|
| **Image** | Dastur va uning muhiti solingan tayyor qolip. O'zgarmaydi | `python:3.14-slim` asosida qurilgan `lms-u12-web` image'i |
| **Konteyner** | Image'dan ishga tushirilgan jonli jarayon | Ishlab turgan Django, PostgreSQL, nginx |
| **Dockerfile** | Image qanday qurilishining retsepti | Loyiha ildizidagi `Dockerfile` |
| **Layer (qatlam)** | Dockerfile'ning har bir buyrug'i yaratadigan qatlam. Docker ularni keshlaydi | Kod o'zgarsa, `pip install` qatlami keshdan olinadi |
| **Volume** | Konteyner tashqarisidagi doimiy xotira | Baza fayllari, yuklangan media, sertifikatlar |
| **Tarmoq** | Konteynerlar bir-birini nomi bilan topadigan ichki tarmoq | Django bazaga `db` nomi bilan ulanadi |
| **Compose** | Bir nechta konteynerni bitta fayl bilan boshqarish | `compose.yaml` |
| **Registry** | Image'lar saqlanadigan ombor (Docker Hub) | `postgres`, `nginx`, `certbot` image'lari shu yerdan keladi |

**Eng muhim qoida:** konteyner o'chsa, uning ichidagi hamma o'zgarish yo'qoladi. Saqlanishi kerak bo'lgan narsa (baza, yuklangan fayllar) albatta **volume**'da turishi kerak.

### 1.4. Bizning tizim

Loyihada to'rtta servis bor. Uchtasi doim ishlab turadi, certbot esa faqat kerak paytda chaqiriladi.

```
                  Internet
                     |
              80, 443 portlar
                     |
         +-----------------------+
         |     nginx             |   /static/ va /media/ ni o'zi beradi
         |  (nginx:1.30-alpine)  |   qolganini web'ga uzatadi
         +-----------------------+
                     |  http://web:8000
         +-----------------------+
         |     web               |   Django + Gunicorn
         |  (Dockerfile'dan)     |
         +-----------------------+
                     |  db:5432
         +-----------------------+
         |     db                |   PostgreSQL 18
         |  (postgres:18-alpine) |
         +-----------------------+

   certbot (certbot/certbot) — SSL sertifikat oladi, doim ishlamaydi
```

Volume'lar (doimiy xotira):

| Volume | Nima saqlanadi | Kim ishlatadi |
|---|---|---|
| `postgres_data` | butun baza | db |
| `static_data` | `collectstatic` yig'gan CSS/JS | web yozadi, nginx o'qiydi |
| `media_data` | foydalanuvchi yuklagan fayllar | web yozadi, nginx o'qiydi |
| `certbot_www` | sertifikat tekshiruvi fayllari | certbot yozadi, nginx o'qiydi |
| `certbot_conf` | SSL sertifikatlar | certbot yozadi, nginx o'qiydi |

Diqqat qiling: **faqat nginx** tashqi portlarni ochadi. Bazaga va Django'ga internetdan to'g'ridan-to'g'ri kirib bo'lmaydi.

---

## 2. Loyihadagi Docker fayllari

Bu fayllar repoda allaqachon bor va **har bir qatori izohlangan**. Darsda ularni ochib, izohlar bo'yicha tushuntirish qulay.

| Fayl | Vazifasi |
|---|---|
| `Dockerfile` | `web` image'i: Python 3.14, paketlar, loyiha kodi, `app` foydalanuvchisi, Gunicorn |
| `entrypoint.sh` | konteyner ko'tarilganda `migrate` va `collectstatic` ni bajaradi, keyin Gunicorn'ni ishga tushiradi |
| `.dockerignore` | image ichiga kirmaydigan fayllar: `.env`, `.venv`, `.git`, `media`, `db.sqlite3` |
| `compose.yaml` | to'rt servis, volume'lar, portlar, ishga tushish tartibi |
| `nginx/http.conf` | 1-bosqich konfigi: faqat HTTP |
| `nginx/https.conf` | 2-bosqich konfigi: HTTP → HTTPS va SSL |

Docker uchun `settings.py` deyarli o'zgarmadi. Faqat ikkita qo'shimcha bor:

1. **`LOGGING` bloki.** `DEBUG=False` bo'lganda Django 500 xatoning tafsilotini hech qayerga yozmaydi. Bu blok xatolarni ekranga chiqaradi, Docker esa ularni yig'adi va `docker compose logs web` da ko'rsatadi.
2. **`accounts/signals.py` dagi `raw` tekshiruvi.** `loaddata` fixture'dan user yuklaganda signal ham profil yaratib, fixture'dagi profil bilan to'qnashadi. Endi `loaddata` paytida signal ishlamaydi.

Django bazani `DB_NAME` bor-yo'qligiga qarab tanlaydi: bor bo'lsa PostgreSQL, yo'q bo'lsa SQLite. Docker'da `DB_HOST` qiymati `db` — bu `compose.yaml` dagi servis nomi.

### 2.1. Sozlamalar qanday yetib boradi

```
.env fayl  ──▶  compose.yaml  ──▶  konteyner ichidagi muhit o'zgaruvchilari  ──▶  settings.py
(qiymatlar)     (qaysi qiymat            (SECRET_KEY, DB_PASSWORD ...)            (os.environ)
                 qayerga ketadi)
```

`.env` fayli git'ga **tushmaydi** va image ichiga ham **kirmaydi**. Har bir serverda o'zining `.env` fayli bo'ladi.

`.env` da bo'ladigan qiymatlar:

```
DEBUG=False
SECRET_KEY=<uzun tasodifiy qiymat>
ALLOWED_HOSTS=<domen>,<server_ip>,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://<domen>
USE_HTTPS=False
SECURE_HSTS_SECONDS=3600
DB_NAME=test_db
DB_USER=test_db_user
DB_PASSWORD=<tasodifiy parol>
NGINX_CONF=http
```

Oxirgi qator — nginx qaysi konfig bilan ishlashini tanlaydi: `http` yoki `https`.

---

## 3. 🖥 LOKAL — kompyuterda sinab ko'rish

Bu bo'lim ixtiyoriy, lekin darsda foydali: o'quvchilar serverga chiqmasdan Docker'ni ko'radi. Kompyuterda **Docker Desktop** o'rnatilgan bo'lishi kerak (docker.com/products/docker-desktop).

Docker ishlayotganini tekshirish:

```bash
docker --version && docker compose version
```

Loyiha papkasiga o'tib, `.env` faylini Docker uchun tayyorlang. Sizda `.env` allaqachon bor (`DEBUG=True` bilan) — Docker uchun unga faqat baza paroli qatorini qo'shish kifoya:

```bash
echo "DB_PASSWORD=lokal-sinov-paroli" >> .env
```

> `DB_NAME` va `DB_USER` uchun `compose.yaml` da standart qiymat bor, shuning uchun ularni yozish shart emas. `.env` da `DB_NAME` yo'qligi uchun oddiy `runserver` avvalgidek SQLite bilan ishlayveradi.

Build qilib, hammasini fonda ishga tushirish (birinchi marta 2-5 daqiqa, paketlar yuklab olinadi):

```bash
docker compose up -d --build
```

Bitta buyruqning o'zi yetadi, chunki `entrypoint.sh` konteyner ichida quyidagilarni avtomatik bajaradi:

1. `python manage.py migrate` — bazada jadvallar yaratiladi
2. `python manage.py collectstatic` — CSS/JS fayllar yig'iladi
3. keyin gunicorn ishga tushadi

Buni loglarda ko'rish mumkin:

```bash
docker compose logs web | head -20
```

`==> Migratsiyalar qo'llanmoqda` va `==> Static fayllar yig'ilmoqda` qatorlari chiqadi.

> Kerak bo'lsa bu buyruqlarni qo'lda ham chaqirsa bo'ladi, masalan darsda alohida ko'rsatish uchun:
> `docker compose exec web python manage.py migrate`

Holatni ko'rish:

```bash
docker compose ps
```

`db` — `healthy`, `web` va `nginx` — `Up` bo'lishi kerak. Brauzerda oching: **http://localhost**

Loglarni kuzatish (`Ctrl+C` bilan chiqish):

```bash
docker compose logs -f web
```

Konteyner ichida buyruq bajarish (masalan, admin yaratish):

```bash
docker compose exec web python manage.py createsuperuser
```

Sinov tugagach to'xtatish. Volume'lar saqlanib qoladi:

```bash
docker compose down
```

Volume'larni ham o'chirish (baza va yuklangan fayllar yo'qoladi):

```bash
docker compose down -v
```

---

## 4. AWS — server tayyorlash

### 4.1. EC2 instance yaratish

EC2 Console → **Launch instance**:

| Maydon | Qiymat |
|---|---|
| Name | `lms-u12-docker` |
| AMI | **Ubuntu Server 24.04 LTS** (x86_64) |
| Instance type | `t3.small` (2 GB RAM) tavsiya. `t3.micro` (1 GB) ham bo'ladi, swap qo'shamiz |
| Key pair | mavjud `.pem` kalitingiz yoki yangi yarating |
| Storage | **30 GB gp3**. Standart 8 GB yetmaydi: Docker image'lari ~1.2 GB, ustiga videolar qo'shiladi |

### 4.2. Security Group — portlar

**Muhim:** har bir qoida uchun `Add rule` tugmasini bosing. Mavjud qatorni tahrirlamang, aks holda eski qoida yo'qoladi va serverga kira olmay qolasiz.

| Type | Protocol | Port | Source |
|---|---|---|---|
| SSH | TCP | 22 | My IP (yoki `0.0.0.0/0`) |
| HTTP | TCP | 80 | Anywhere-IPv4 (`0.0.0.0/0`) |
| HTTPS | TCP | 443 | Anywhere-IPv4 (`0.0.0.0/0`) |

Yakunda **Inbound rules (3)** bo'lishi kerak.

> 5432 (PostgreSQL) va 8000 (Gunicorn) portlarini **ochmang**. Ularga faqat Docker ichki tarmog'idan kiriladi.

### 4.3. Elastic IP — bu qadamni o'tkazib yubormang

Oddiy public IP server to'xtatib qayta yoqilganda **o'zgaradi**. Domen esa eski IP'ga qarab turadi va sayt ochilmay qoladi.

EC2 Console → **Elastic IPs** → `Allocate Elastic IP address` → yaratilgan manzilni belgilab → `Actions` → `Associate Elastic IP address` → instance'ni tanlang.

Shundan keyin serverning IP manzili doimiy bo'ladi.

### 4.4. 🖥 LOKAL — kalit huquqi va ulanish

SSH ochiq huquqli kalitni rad etadi:

```bash
chmod 400 ~/Downloads/django-key.pem
```

Ulanishni tekshirish:

```bash
ssh -i ~/Downloads/django-key.pem ubuntu@13.60.107.7 'echo SSH ishladi'
```

`SSH ishladi` chiqsa — davom eting. `Operation timed out` chiqsa, Security Group'da 22-port yopiq.

> **`REMOTE HOST IDENTIFICATION HAS CHANGED` xatosi.** Server qayta yaratilgan yoki Elastic IP boshqa instance'ga ulangan bo'lsa chiqadi. Eski kalitni o'chirib qayta ulaning: `ssh-keygen -R 13.60.107.7`

---

## 5. ☁️ SERVER — tizimni tayyorlash

Serverga kiring:

```bash
ssh -i ~/Downloads/django-key.pem ubuntu@13.60.107.7
```

### 5.1. Swap qo'shish

1 GB RAM'li serverda image build qilish xotira yetmay to'xtashi mumkin. 2 GB swap buni oldini oladi. (`t3.small` da ham qo'shib qo'yish zarar qilmaydi.)

```bash
sudo fallocate -l 2G /swapfile
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

Server qayta yuklanganda ham qolishi uchun:

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Tekshirish:

```bash
free -h
```

### 5.2. Docker o'rnatish

Ubuntu'ning o'z omborida Docker'ning eski versiyasi bor va `docker compose` plagini yo'q. Shuning uchun Docker'ning rasmiy omborini qo'shamiz.

Ombor kalitini o'rnatish:

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl
```

```bash
sudo install -m 0755 -d /etc/apt/keyrings
```

```bash
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
```

```bash
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Omborni qo'shish:

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Docker va plaginlarini o'rnatish:

```bash
sudo apt-get update
```

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Tekshirish:

```bash
sudo docker --version && sudo docker compose version
```

### 5.3. `sudo` yozmaslik uchun

`ubuntu` foydalanuvchisini `docker` guruhiga qo'shamiz:

```bash
sudo usermod -aG docker ubuntu
```

**Guruh faqat yangi sessiyada kuchga kiradi.** Serverdan chiqib, qayta kiring:

```bash
exit
```

```bash
ssh -i ~/Downloads/django-key.pem ubuntu@13.60.107.7
```

Endi `sudo` siz ishlashini tekshiring:

```bash
docker run --rm hello-world
```

> **Xavfsizlik eslatmasi:** `docker` guruhidagi foydalanuvchi amalda root huquqiga ega bo'ladi (konteynerga butun diskni ulab, hamma faylni o'qib chiqishi mumkin). Serverga kirish huquqini faqat ishonchli odamlarga bering.

---

## 6. ☁️ SERVER — kod va sozlamalar

### 6.1. Kodni klonlash

```bash
sudo mkdir -p /srv/lms-u12 && sudo chown ubuntu:ubuntu /srv/lms-u12
```

```bash
git clone https://github.com/temuralidavron/LMS-U12.git /srv/lms-u12
```

Fayllar kelganini tekshiring:

```bash
ls /srv/lms-u12
```

`Dockerfile`, `compose.yaml`, `nginx` ro'yxatda bo'lishi kerak.

> Repo private bo'lsa: GitHub'da **Deploy key** yarating (`ssh-keygen -t ed25519 -f ~/.ssh/deploy_key`, public kalitni repo Settings → Deploy keys ga qo'shing) va SSH manzil bilan klonlang.

### 6.2. `.env` faylini yaratish

Maxfiy kalit va baza parolini serverning o'zida generatsiya qilamiz. Bitta buyruq bilan `.env` to'liq yoziladi:

```bash
cd /srv/lms-u12 && printf 'DEBUG=False\nSECRET_KEY=%s\nALLOWED_HOSTS=13.60.107.7,localhost,127.0.0.1\nCSRF_TRUSTED_ORIGINS=\nUSE_HTTPS=False\nSECURE_HSTS_SECONDS=3600\nDB_NAME=test_db\nDB_USER=test_db_user\nDB_PASSWORD=%s\nNGINX_CONF=http\n' "$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')" "$(openssl rand -hex 24)" > .env
```

Faylni faqat o'zingiz o'qiy olishini ta'minlang:

```bash
chmod 600 /srv/lms-u12/.env
```

Natijani ko'rish (parol ko'rinadi, ekranni boshqa hech kim ko'rmasin):

```bash
cat /srv/lms-u12/.env
```

> **Nega `secrets.token_urlsafe`?** U faqat harf, raqam, `-` va `_` belgilaridan iborat qiymat beradi. Django'ning `get_random_secret_key()` funksiyasi esa `$` belgisini ham ishlatadi. Compose `.env` dagi `$` ni o'zgaruvchi boshlanishi deb o'qiydi va kalitni sezdirmay buzadi — keyin sessiya va CSRF ishlamay qoladi.

Compose sozlamalarni to'g'ri o'qiyotganini tekshirish (xato bo'lsa, shu yerda aytadi):

```bash
cd /srv/lms-u12 && docker compose config --quiet && echo "compose fayli to'g'ri"
```

---

## 7. DNS — domenni serverga qaratish

Bu qadamni sertifikat olishdan **oldin** bajarish kerak: Let's Encrypt domen sizniki ekanini shu orqali tekshiradi.

Domen panelida (ahost.uz, Cloudflare, GoDaddy, Namecheap va h.k.) **DNS** bo'limiga kirib yangi yozuv qo'shing:

| Maydon | Subdomen uchun (`lms.example.uz`) | Apex uchun (`example.uz`) |
|---|---|---|
| Type | `A` | `A` |
| Name / Host | `lms` | `@` |
| Value / Points to | `13.60.107.7` | `13.60.107.7` |
| TTL | `300` | `300` |

> Cloudflare ishlatsangiz proxy (to'q sariq bulut) belgisini **o'chiring** (DNS only). Yoqiq bo'lsa certbot tekshiruvidan o'tolmaydi.

DNS tarqalishini kuting (5-30 daqiqa), keyin 🖥 LOKAL tekshiring:

```bash
dig +short <DOMEN>
```

Natija aynan `13.60.107.7` bo'lishi kerak. **Bu qadam tugamasdan 10-bo'limga o'tmang.**

> **Darsda yangi subdomen ishlatish tavsiya etiladi.** Avval HTTPS bilan ishlagan domenda brauzerlar HSTS qoidasini eslab qolgan bo'lishi mumkin. Unda darsning HTTP bosqichida brauzer saytni majburan HTTPS'ga burib, sertifikat hali yo'qligi uchun "ochilmadi" deb ko'rsatadi.

---

## 8. ☁️ SERVER — 1-bosqich: saytni HTTP orqali ko'tarish

Tartib lokal sinovdagi bilan aynan bir xil, buyruq ham bitta.

### 8.1. Build qilish va ishga tushirish

```bash
cd /srv/lms-u12 && docker compose up -d --build
```

Birinchi marta 2-4 daqiqa ketadi: Docker image'larni yuklab oladi va paketlarni o'rnatadi.

Bu bitta buyruq ichida nimalar bo'ladi:

| Tartib | Nima bo'ladi | Kim qiladi |
|---|---|---|
| 1 | `web` image'i quriladi | `docker compose build` qismi |
| 2 | `db` ko'tariladi va `healthy` bo'lishi kutiladi | `compose.yaml` dagi `depends_on` |
| 3 | migratsiyalar qo'llanadi | `entrypoint.sh` |
| 4 | static fayllar yig'iladi | `entrypoint.sh` |
| 5 | gunicorn ishga tushadi | Dockerfile'dagi `CMD` |
| 6 | nginx ko'tariladi | `compose.yaml` |

### 8.2. Nima bo'lganini loglarda ko'rish

```bash
cd /srv/lms-u12 && docker compose logs web | head -20
```

`==> Migratsiyalar qo'llanmoqda`, migratsiya qatorlari, `==> Static fayllar yig'ilmoqda` va oxirida gunicorn'ning `Listening at: http://0.0.0.0:8000` qatori chiqishi kerak.

### 8.3. Holat

```bash
cd /srv/lms-u12 && docker compose ps
```

Kutilgan holat:

| Servis | Holat |
|---|---|
| `db` | `Up ... (healthy)` |
| `web` | `Up ...` |
| `nginx` | `Up ...`, portlar: `0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp` |

`db` va `web` da tashqi port yo'q — shundayligi to'g'ri.

### 8.5. Tekshirish

☁️ SERVER — ichkaridan:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1/accounts/login/
```

🖥 LOKAL — tashqaridan:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://13.60.107.7/accounts/login/
```

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://13.60.107.7/static/css/style.css
```

Uchalasi ham `200` qaytarishi kerak. Brauzerda oching: **http://13.60.107.7**

Loglarni ko'rish:

```bash
cd /srv/lms-u12 && docker compose logs web | tail -20
```

Gunicorn ishga tushganini bildiruvchi qatorlar: `Starting gunicorn`, `Listening at: http://0.0.0.0:8000`, `Booting worker`.

---

## 9. Ma'lumot va media fayllarni ko'chirish

Lokal kompyuterdagi baza SQLite'da, serverda esa PostgreSQL. Ma'lumotni `data.json` fayli orqali ko'chiramiz. Media fayllar git'da yo'q, ular alohida yuboriladi.

### 9.1. 🖥 LOKAL — ma'lumotni eksport qilish

`data.json` allaqachon bor bo'lsa, bu qadamni o'tkazib yuboring. Yangilash kerak bo'lsa:

```bash
.venv/bin/python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e sessions --indent 2 -o data.json
```

`-e sessions` — sessiyalar ko'chirilmaydi, ular vaqtinchalik. `contenttypes` va `auth.Permission` ni ham chiqarib tashlaymiz: ularni Django `migrate` paytida o'zi yaratadi, ko'chirilsa ID'lar to'qnashadi.

### 9.2. 🖥 LOKAL — serverga yuborish

```bash
scp -i ~/Downloads/django-key.pem data.json ubuntu@13.60.107.7:~/
```

```bash
scp -i ~/Downloads/django-key.pem -r media ubuntu@13.60.107.7:~/
```

### 9.3. ☁️ SERVER — ma'lumotni yuklash

Fayl konteyner ichiga ko'chirilmaydi, uning mazmuni to'g'ridan-to'g'ri buyruqqa uzatiladi. `-T` — terminal ajratmaslik (fayl uzatishda shart), oxiridagi `-` esa "ma'lumot fayldan emas, kirishdan keladi" degani:

```bash
cd /srv/lms-u12 && docker compose exec -T web python manage.py loaddata --format=json - < ~/data.json
```

`Installed 81 object(s) from 1 fixture(s)` kabi javob chiqadi. Tekshirish:

```bash
cd /srv/lms-u12 && docker compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model as g; print('Userlar:', g().objects.count())"
```

### 9.4. ☁️ SERVER — media fayllarni volume'ga ko'chirish

```bash
cd /srv/lms-u12 && docker compose cp ~/media/. web:/app/media/
```

Fayllar ko'chirilganda ularning egasi sizning kompyuteringizdagi foydalanuvchi bo'lib qoladi, konteyner ichidagi `app` esa ularga yoza olmaydi. Shuning uchun egalikni to'g'rilaymiz (`-u root` — bu buyruqni root nomidan bajarish):

```bash
cd /srv/lms-u12 && docker compose exec -u root web chown -R app:app /app/media
```

Tekshirish — hamma qatorda `app app` bo'lishi kerak:

```bash
cd /srv/lms-u12 && docker compose exec web ls -la /app/media /app/media/courses
```

Brauzerda yoki curl bilan (o'zingizdagi fayl nomini yozing):

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://13.60.107.7/media/courses/1000074614.jpg
```

> **Bu qadamni o'tkazib yuborsangiz:** eski fayllar 404 bo'ladi va yangi fayl yuklashda `Permission denied` xatosi chiqadi.

### 9.5. ☁️ SERVER — `data.json` ni o'chirish

Faylda parollar (hash holida) bor, serverda yotishi kerak emas:

```bash
rm ~/data.json
```

### 9.6. ☁️ SERVER — admin

Ma'lumot import qilingan bo'lsa, eski adminlar allaqachon bor. Yangi admin kerak bo'lsa:

```bash
cd /srv/lms-u12 && docker compose exec web python manage.py createsuperuser
```

`CustomUser` da `role` maydoni bor va sukut bo'yicha `student` bo'ladi. Superuserlarning rolini `admin` ga qo'yish:

```bash
cd /srv/lms-u12 && docker compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); print('updated', U.objects.filter(is_superuser=True).update(role='admin'))"
```

---

## 10. ☁️ SERVER — 2-bosqich: HTTPS

Bu bo'limni 8-bo'lim tugagandan (sayt IP orqali ishlayapti) va 7-bo'limdagi DNS tayyor bo'lganidan keyin bajaring.

### 10.1. Shartlarni tekshirish

🖥 LOKAL — domen serverga qarayaptimi:

```bash
dig +short <DOMEN>
```

🖥 LOKAL — 443-port Security Group'da ochiqmi:

```bash
nc -z -G 10 13.60.107.7 443 && echo "443 OCHIQ" || echo "443 YOPIQ"
```

`443 YOPIQ` bo'lsa, 4.2-bo'limga qaytib portni oching. **Sertifikat olishdan oldin ochilgan bo'lishi kerak**, aks holda nginx HTTPS'ga yo'naltirgandan keyin sayt butunlay ochilmay qoladi.

### 10.2. Domenni Django'ga tanitish

Hozir `.env` da faqat IP bor. Domen bilan kelgan so'rovga Django `400 Bad Request` qaytaradi. Domenni qo'shamiz:

```bash
cd /srv/lms-u12 && sed -i 's|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=<DOMEN>,13.60.107.7,localhost,127.0.0.1|' .env
```

`.env` o'zgargani uchun `web` konteynerini qayta yaratamiz (compose o'zi buni qiladi):

```bash
cd /srv/lms-u12 && docker compose up -d web
```

Tekshirish — `200` bo'lishi kerak:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://<DOMEN>/accounts/login/
```

### 10.3. Avval test (staging) sertifikati

Let's Encrypt bir hafta ichida bitta domenga beriladigan sertifikat sonini cheklaydi. Sozlamada xato bo'lsa, limitni behuda sarflab qo'yish mumkin. Shuning uchun avval limitga kirmaydigan test sertifikatini olamiz:

```bash
cd /srv/lms-u12 && docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d <DOMEN> --cert-name lms --email <EMAIL> --agree-tos --no-eff-email --staging
```

Buyruq qismlari:

| Qism | Ma'nosi |
|---|---|
| `run --rm certbot` | certbot konteynerini bir marta ishlatib, keyin o'chirish |
| `certonly` | faqat sertifikat olish, konfigni o'zgartirmaslik |
| `--webroot -w /var/www/certbot` | tekshiruv faylini shu papkaga yozish. Nginx uni `/.well-known/acme-challenge/` manzilida beradi |
| `-d <DOMEN>` | sertifikat qaysi domen uchun |
| `--cert-name lms` | sertifikat papkasining nomi. Shu sabab nginx konfigida domen yozilmaydi |
| `--email` | muddat tugashi haqida ogohlantirish keladigan manzil |
| `--agree-tos --no-eff-email` | shartlarga rozilik, reklama xatlariga yozilmaslik |
| `--staging` | test serveri, limitga kirmaydi |

`Successfully received certificate` chiqsa — sozlama to'g'ri.

### 10.4. Haqiqiy sertifikat

Test sertifikatini o'chirib, haqiqiysini olamiz:

```bash
cd /srv/lms-u12 && docker compose run --rm certbot delete --cert-name lms
```

```bash
cd /srv/lms-u12 && docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d <DOMEN> --cert-name lms --email <EMAIL> --agree-tos --no-eff-email
```

Sertifikatni ko'rish:

```bash
cd /srv/lms-u12 && docker compose run --rm certbot certificates
```

### 10.5. Nginx va Django'ni HTTPS'ga o'tkazish

Uch qiymat birdan o'zgaradi: nginx konfigi, Django'ning HTTPS rejimi va CSRF manzili.

```bash
cd /srv/lms-u12 && sed -i -e 's|^NGINX_CONF=.*|NGINX_CONF=https|' -e 's|^USE_HTTPS=.*|USE_HTTPS=True|' -e 's|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=https://<DOMEN>|' .env
```

Natijani ko'rish:

```bash
grep -E "^(DEBUG|ALLOWED_HOSTS|CSRF_TRUSTED_ORIGINS|USE_HTTPS|SECURE_HSTS_SECONDS|NGINX_CONF)=" /srv/lms-u12/.env
```

Qo'llash. Compose `nginx` uchun boshqa konfig fayli ulanganini va `web` uchun o'zgaruvchi o'zgarganini o'zi sezadi, ikkalasini qayta yaratadi:

```bash
cd /srv/lms-u12 && docker compose up -d
```

### 10.6. Tekshirish

🖥 LOKAL — HTTP avtomatik HTTPS'ga o'tyaptimi (`301` va `Location: https://...`):

```bash
curl -sI http://<DOMEN>/accounts/login/ | head -3
```

🖥 LOKAL — HTTPS javobi (`200`):

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://<DOMEN>/accounts/login/
```

🖥 LOKAL — sertifikat ma'lumoti:

```bash
echo | openssl s_client -connect <DOMEN>:443 -servername <DOMEN> 2>/dev/null | openssl x509 -noout -issuer -dates
```

☁️ SERVER — Django prod tekshiruvi:

```bash
cd /srv/lms-u12 && docker compose exec web python manage.py check --deploy
```

Faqat bitta ogohlantirish qolishi kerak: `security.W021` (HSTS preload). Bu ataylab yoqilmagan, qaytarib bo'lmaydigan qadam.

Brauzerda oching: **https://<DOMEN>** — qulf belgisi ko'rinishi kerak.

### 10.7. HSTS haqida

`.env` da `SECURE_HSTS_SECONDS=3600` turibdi. Bu brauzerga "shu domenga bir soat davomida faqat HTTPS orqali kir" deydi. Qiymat ataylab kichik: brauzer buni **eslab qoladi** va sertifikatda muammo chiqsa, foydalanuvchi saytga umuman kira olmaydi.

Bir necha kun muammosiz ishlagach, qiymatni oshirish mumkin (1 yil):

```bash
cd /srv/lms-u12 && sed -i 's|^SECURE_HSTS_SECONDS=.*|SECURE_HSTS_SECONDS=31536000|' .env && docker compose up -d web
```

---

## 11. ☁️ SERVER — sertifikatni avtomatik yangilash

Sertifikat cheklangan muddat amal qiladi. `certbot renew` muddat tugashiga oz qolganda uni yangilaydi, muddat yaqin bo'lmasa hech narsa qilmaydi. Shuning uchun uni har kuni ishga tushirish xavfsiz.

Yangilash ishlashini oldin sinab ko'ramiz (haqiqiy yangilamaydi):

```bash
cd /srv/lms-u12 && docker compose run --rm certbot renew --dry-run
```

`Congratulations, all simulated renewals succeeded` chiqishi kerak.

Kunlik vazifani qo'shish (har kuni 03:00 da):

```bash
(crontab -l 2>/dev/null; echo '0 3 * * * cd /srv/lms-u12 && /usr/bin/docker compose run --rm certbot renew --quiet && /usr/bin/docker compose exec -T nginx nginx -s reload') | crontab -
```

Nima uchun oxirida `nginx -s reload`: certbot yangi sertifikat faylini yozadi, lekin ishlab turgan nginx eski faylni xotirasida saqlab turadi. `reload` uni saytni to'xtatmasdan qayta o'qishga majbur qiladi.

Tekshirish:

```bash
crontab -l
```

> Cron'da `docker` ning to'liq yo'li yozilgan (`/usr/bin/docker`). Cron muhitida `PATH` qisqa bo'ladi va qisqa nom topilmasligi mumkin.

---

## 12. ☁️ SERVER — yangilanish chiqarish (redeploy)

Kod o'zgargach, 🖥 LOKAL:

```bash
git push
```

Keyin ☁️ SERVER — ikki buyruq:

```bash
cd /srv/lms-u12 && git pull
```

```bash
cd /srv/lms-u12 && docker compose up -d --build
```

Migratsiya va `collectstatic` ni eslab qolish shart emas: yangi konteyner ko'tarilayotganda `entrypoint.sh` ularni o'zi bajaradi. Sayt faqat bir necha soniya uzilib turadi.

Natijani ko'rish:

```bash
cd /srv/lms-u12 && docker compose logs web | head -20
```

> **Nginx konfigi o'zgarganda** (`nginx/http.conf` yoki `nginx/https.conf`) qo'shimcha buyruq kerak:
>
> ```bash
> cd /srv/lms-u12 && docker compose restart nginx
> ```
>
> Sababi: konfig fayli konteynerga bitta fayl sifatida ulangan. `git pull` faylni yangisiga almashtiradi, ishlab turgan konteyner esa eski faylni ushlab turadi. `restart` faylni qaytadan ulaydi.

Yangilanishdan keyin tekshirish:

```bash
cd /srv/lms-u12 && docker compose ps && curl -s -o /dev/null -w "%{http_code}\n" https://<DOMEN>/accounts/login/
```

---

## 13. ☁️ SERVER — zaxira nusxa va tiklash

Baza va media fayllar volume'larda. Volume'lar `docker compose down` dan keyin ham qoladi, lekin server o'chirilsa yoki disk buzilsa yo'qoladi. Shuning uchun zaxira nusxa kerak.

### 13.1. Zaxira nusxa olish

```bash
mkdir -p ~/backups
```

Baza (`pg_dump` konteyner ichida ishlaydi, natija serverdagi faylga yoziladi):

```bash
cd /srv/lms-u12 && docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > ~/backups/db-$(date +%F).sql.gz
```

Media fayllar:

```bash
cd /srv/lms-u12 && docker compose exec -T web tar czf - -C /app media > ~/backups/media-$(date +%F).tar.gz
```

Tekshirish:

```bash
ls -lh ~/backups
```

> Zaxira nusxalarni serverdan tashqariga ham ko'chirib qo'ying. 🖥 LOKAL:
> `scp -i ~/Downloads/django-key.pem ubuntu@13.60.107.7:~/backups/* ./backups/`

### 13.2. Kunlik avtomatik zaxira

Har kuni 02:00 da baza nusxasini olish va 14 kundan oshganini o'chirish:

```bash
(crontab -l 2>/dev/null; echo '0 2 * * * cd /srv/lms-u12 && /usr/bin/docker compose exec -T db sh -c "pg_dump -U \$POSTGRES_USER \$POSTGRES_DB" | gzip > /home/ubuntu/backups/db-$(date +\%F).sql.gz && find /home/ubuntu/backups -name "db-*.sql.gz" -mtime +14 -delete') | crontab -
```

> Cron'da `%` belgisi maxsus ma'noga ega, shuning uchun `\%F` deb yozilgan.

### 13.3. Bazani tiklash

Tiklash paytida hech kim bazaga yozmasligi kerak, shuning uchun avval `web` to'xtatiladi:

```bash
cd /srv/lms-u12 && docker compose stop web
```

Bazani bo'shatib, yangisini yaratamiz:

```bash
cd /srv/lms-u12 && docker compose exec -T db sh -c 'dropdb -U "$POSTGRES_USER" "$POSTGRES_DB" && createdb -U "$POSTGRES_USER" "$POSTGRES_DB"'
```

Nusxani yuklaymiz (fayl nomini o'zingizdagiga almashtiring):

```bash
cd /srv/lms-u12 && gunzip -c ~/backups/db-2026-09-19.sql.gz | docker compose exec -T db sh -c 'psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' > /dev/null
```

```bash
cd /srv/lms-u12 && docker compose start web
```

### 13.4. Media fayllarni tiklash

```bash
cd /srv/lms-u12 && docker compose exec -T -u root web tar xzf - -C /app < ~/backups/media-2026-09-19.tar.gz
```

```bash
cd /srv/lms-u12 && docker compose exec -u root web chown -R app:app /app/media
```

Tekshirish:

```bash
cd /srv/lms-u12 && docker compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model as g; from courses.models import Course; print('userlar:', g().objects.count(), 'kurslar:', Course.objects.count())"
```

---

## 14. Muammolarni hal qilish

Har bir muammo uchun: qanday ko'rinadi → sababi → nima qilish.

### 502 Bad Gateway

Nginx ishlayapti, lekin Django javob bermayapti.

```bash
cd /srv/lms-u12 && docker compose ps
```

```bash
cd /srv/lms-u12 && docker compose logs web | tail -30
```

`web` `Up` bo'lmasa, loglarda sabab yozilgan bo'ladi (ko'pincha `.env` da xato qiymat yoki kodda sintaksis xatosi).

### 500 Internal Server Error

Django ichidagi xato. Traceback loglarda:

```bash
cd /srv/lms-u12 && docker compose logs web | tail -50
```

Xatoni brauzerda batafsil ko'rish uchun `.env` da vaqtincha `DEBUG=True` qilib `docker compose up -d web` bajarish mumkin. **Tekshirgach albatta `False` ga qaytaring.**

### 400 Bad Request (`DisallowedHost`)

Murojaat qilinayotgan domen `ALLOWED_HOSTS` da yo'q.

```bash
grep ALLOWED_HOSTS /srv/lms-u12/.env
```

Domenni qo'shib, `docker compose up -d web` bajaring.

### CSS yuklanmayapti (sayt "yalang'och" ko'rinadi)

Odatda `collectstatic` bajarilmagan bo'ladi. Uni `entrypoint.sh` o'zi bajaradi, shuning uchun avval loglarga qarang:

```bash
cd /srv/lms-u12 && docker compose logs web | grep -A3 "Static fayllar"
```

Fayllar joyidami:

```bash
cd /srv/lms-u12 && docker compose exec nginx ls /app/staticfiles
```

Bo'sh bo'lsa, qo'lda bajaring:

```bash
cd /srv/lms-u12 && docker compose exec web python manage.py collectstatic --noinput
```

### Media fayllar 404 yoki yuklashda `Permission denied`

```bash
cd /srv/lms-u12 && docker compose exec web ls -la /app/media
```

Papkalar egasi `app` bo'lmasa:

```bash
cd /srv/lms-u12 && docker compose exec -u root web chown -R app:app /app/media
```

### `ERR_TOO_MANY_REDIRECTS` (cheksiz yo'naltirish)

Django so'rov HTTPS orqali kelganini bilmayapti va uni qayta-qayta HTTPS'ga yuboryapti. Nginx `X-Forwarded-Proto` yuborayotganini tekshiring:

```bash
grep X-Forwarded-Proto /srv/lms-u12/nginx/https.conf
```

`settings.py` da `USE_HTTPS` bloki ichida `SECURE_PROXY_SSL_HEADER` borligini tekshiring. Ikkalasi joyida bo'lsa, `docker compose restart nginx` va `docker compose up -d web`.

### Nginx ishga tushmayapti: `cannot load certificate`

`.env` da `NGINX_CONF=https`, lekin sertifikat hali olinmagan.

```bash
cd /srv/lms-u12 && docker compose logs nginx | tail -5
```

Sertifikat olinmagan bo'lsa, vaqtincha HTTP bosqichiga qaytib oling:

```bash
cd /srv/lms-u12 && sed -i 's|^NGINX_CONF=.*|NGINX_CONF=http|' .env && docker compose up -d nginx
```

Keyin 10.3-bo'limdan davom eting.

### Nginx `Is a directory` xatosi bilan yiqildi

`.env` dagi `NGINX_CONF` qiymati xato yozilgan (masalan `Https` yoki `http.conf`). Bunda Docker mavjud bo'lmagan fayl o'rniga **papka** yaratib qo'yadi.

```bash
grep NGINX_CONF /srv/lms-u12/.env
```

Faqat `http` yoki `https` bo'lishi kerak. Docker yaratgan keraksiz papkani o'chirish:

```bash
ls -la /srv/lms-u12/nginx/
```

### Nginx konfigidagi o'zgarish ta'sir qilmayapti

`git pull` dan keyin:

```bash
cd /srv/lms-u12 && docker compose restart nginx
```

Konteyner ichidagi faylni tekshirish:

```bash
cd /srv/lms-u12 && docker compose exec nginx cat /etc/nginx/conf.d/default.conf | head -20
```

### `permission denied while trying to connect to the Docker daemon socket`

`docker` guruhi hali kuchga kirmagan. Serverdan chiqib qayta kiring (5.3-bo'lim).

### `required variable DB_PASSWORD is missing a value`

`.env` fayli yo'q yoki unda `DB_PASSWORD` yozilmagan. Compose buni hamma buyruqda aytadi.

```bash
ls -la /srv/lms-u12/.env && grep -c DB_PASSWORD /srv/lms-u12/.env
```

### Baza bo'm-bo'sh chiqdi

Ikki sabab bo'ladi:

1. `docker compose down -v` bajarilgan — `-v` volume'larni o'chiradi.
2. `compose.yaml` da volume yo'li `/var/lib/postgresql/data` deb yozilgan. PostgreSQL 18 da to'g'ri yo'l `/var/lib/postgresql`.

Volume joyidami:

```bash
docker volume ls | grep lms-u12
```

Baza ichida nima borligini ko'rish:

```bash
cd /srv/lms-u12 && docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"' | head -20
```

### `Bind for 0.0.0.0:80 failed: port is already allocated`

80-portni boshqa dastur egallagan (masalan, avval o'rnatilgan nginx):

```bash
sudo ss -tlnp | grep -E ':(80|443)'
```

Serverga nginx apt orqali o'rnatilgan bo'lsa, o'chiring:

```bash
sudo systemctl disable --now nginx
```

### Disk to'lib qoldi

```bash
df -h /
```

```bash
docker system df
```

Ishlatilmayotgan image va build keshini o'chirish (volume'larga tegmaydi):

```bash
docker system prune -a -f
```

### Build paytida jarayon o'ldirildi (xotira yetmadi)

```bash
free -h
```

```bash
sudo journalctl -k | grep -i "out of memory" | tail
```

Swap qo'shilmagan bo'lsa — 5.1-bo'lim.

### Certbot: `Connection refused` yoki `Timeout during connect`

Let's Encrypt serveringizga 80-port orqali kira olmayapti. Uchta sababi bo'ladi:

1. DNS hali tarqalmagan — `dig +short <DOMEN>` natijasini tekshiring.
2. 80-port Security Group'da yopiq.
3. Nginx ishlamayapti — `docker compose ps`.

### Certbot: `too many certificates already issued`

Bir hafta ichida bitta domen uchun sertifikat olish limiti tugagan. Limit bir hafta ichida o'zi tiklanadi. Shu sabab sozlamani avval `--staging` bilan sinash kerak (10.3-bo'lim).

---

## 15. Xavfsizlik

### 15.1. Portlar

Faqat nginx 80 va 443 portlarni ochadi. **Bazaga `ports` qo'shmang.** Docker `ports` bilan ochilgan port serverdagi `ufw` firewall qoidalarini chetlab o'tadi: `ufw` yopiq deb ko'rsatsa ham, port amalda internetdan ochiq bo'ladi. Shuning uchun haqiqiy to'siq — AWS Security Group.

Tekshirish:

```bash
cd /srv/lms-u12 && docker compose ps
```

`db` va `web` qatorlarida `0.0.0.0:...` ko'rinmasligi kerak.

### 15.2. `.env` fayli

```bash
ls -l /srv/lms-u12/.env
```

`-rw-------` (600) bo'lishi kerak. Fayl git'da ham, image ichida ham yo'q.

> Muhit o'zgaruvchilari `docker inspect` orqali ko'rinadi. Bu Docker'ning odatiy ishlashi. Serverga kirish huquqi bor odam baribir `.env` ni o'qiy oladi, shuning uchun serverga kirishni cheklash muhim.

### 15.3. SSH

Deploy tugagach, Security Group'dagi SSH qoidasini `My IP` ga o'zgartiring.

### 15.4. Tizim yangilanishlari

```bash
sudo apt-get install -y unattended-upgrades
```

```bash
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 15.5. Image versiyalari

`compose.yaml` da versiyalar aniq yozilgan (`postgres:18-alpine`, `nginx:1.30-alpine`). Vaqti-vaqti bilan yangi versiyaga o'tib, xavfsizlik tuzatishlarini oling:

```bash
cd /srv/lms-u12 && docker compose pull && docker compose up -d
```

### 15.6. Yuklangan fayllar

Foydalanuvchi yuklagan fayllar sayt bilan bir domendan beriladi. Fayl turini cheklash (masalan, faqat `pdf`, `jpg`, `mp4`) loyiha darajasidagi alohida ish — bu qo'llanma doirasidan tashqarida.

---

## 16. Foydali buyruqlar

Hammasi `/srv/lms-u12` papkasida bajariladi.

Holat:

```bash
docker compose ps
```

Loglar (jonli kuzatish, `Ctrl+C` bilan chiqish):

```bash
docker compose logs -f web
```

Faqat oxirgi 50 qator:

```bash
docker compose logs --tail 50 web
```

Django shell:

```bash
docker compose exec web python manage.py shell
```

Bazaga psql orqali kirish:

```bash
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Konteyner ichiga kirish (Linux buyruqlari bilan ko'rish):

```bash
docker compose exec web bash
```

Bitta servisni qayta ishga tushirish:

```bash
docker compose restart web
```

Hammasini to'xtatish (volume'lar saqlanadi):

```bash
docker compose down
```

Resurs sarfi:

```bash
docker stats --no-stream
```

Disk:

```bash
docker system df
```

Volume'lar ro'yxati:

```bash
docker volume ls | grep lms-u12
```

Sertifikat holati:

```bash
docker compose run --rm certbot certificates
```

### Fayllar joylashuvi (server)

| Yo'l | Nima |
|---|---|
| `/srv/lms-u12/` | loyiha kodi (git'dan) |
| `/srv/lms-u12/.env` | maxfiy sozlamalar (600) |
| `/srv/lms-u12/compose.yaml` | servislar tavsifi |
| `/srv/lms-u12/nginx/` | nginx konfiglari |
| `~/backups/` | zaxira nusxalar |
| `/swapfile` | 2 GB swap |
| Docker volume'lari | `docker volume ls` (baza, media, static, sertifikatlar) |

### Ikki usulni solishtirish

| | `DEPLOY.md` (Docker'siz) | `DOCKER-DEPLOY.md` (Docker) |
|---|---|---|
| Serverga o'rnatiladi | Python, venv, PostgreSQL, nginx, certbot | faqat Docker |
| Sozlash | systemd servis, nginx konfigi, PostgreSQL user | bitta `compose.yaml` |
| Ishga tushirish | `systemctl restart lms-u12` | `docker compose up -d` |
| Yangilanish | `git pull`, `pip install`, `migrate`, `restart` | `git pull`, `build`, `migrate`, `up -d` |
| Lokal va serverda bir xillik | Python versiyalari farq qiladi | image bir xil |
| Serverni tozalash | qiyin | `docker compose down -v` |
| Qo'shimcha xarajat | — | image'lar diskda ~1.2 GB |
