# Shu serverni sozlash tartibi

`DOCKER-DEPLOY.md` — o'quvchilar uchun to'liq qo'llanma, unda har bir narsaning izohi bor.
Bu fayl — **aynan shu serverga** tegishli qadamlar ro'yxati: nima bajarilgan, nima qolgan, qaysi buyruq qayerda ishlaydi.

## Serverning ma'lumotlari

| Nima | Qiymat |
|---|---|
| Region | `eu-north-1` (Stockholm) |
| Instance | `django` — `i-0aeda94c8d901de53`, `t3.micro` |
| Elastic IP | `13.60.107.7` |
| Private IP | `172.31.24.132` |
| Security Group | `launch-wizard-1` — `sg-0ce10a173903cff45` |
| SSH kalit | `~/Downloads/django-key.pem` |
| SSH buyrug'i | `ssh -i ~/Downloads/django-key.pem ubuntu@13.60.107.7` |
| OS | Ubuntu 24.04.4 LTS, x86_64 |
| RAM | 911 MB |
| Loyiha papkasi | `/srv/lms-u12` |
| Baza | `test_db` / `test_db_user` |
| GitHub | `https://github.com/temuralidavron/LMS-U12.git` |
| Domen (sinov) | to'ldirilmagan |
| Domen (dars) | to'ldirilmagan |
| Let's Encrypt email | to'ldirilmagan |

## Holat

| № | Qadam | Qayerda | Holat |
|---|---|---|---|
| 1 | Elastic IP ajratish va biriktirish | AWS Console | ✅ bajarildi |
| 2 | Security Group: 80 va 443 portlar | AWS Console | ✅ bajarildi |
| 3 | Disk 8 GB dan 30 GB ga | AWS Console | ✅ bajarildi |
| 4 | Diskni serverda kengaytirish | server | ✅ bajarildi (29 GB) |
| 5 | Serverdagi eski nginx (apt) o'chirildi | server | ✅ bajarildi |
| 6 | Swap qo'shish | server | ✅ bajarildi (2 GB) |
| 7 | Docker o'rnatish | server | ✅ bajarildi |
| 8 | Lokalda Docker'da sinash | lokal | ✅ bajarildi |
| 9 | Kodni GitHub'ga push qilish | lokal | ⬜ qoldi |
| 10 | Kodni serverga klonlash va `.env` | server | ⬜ qoldi |
| 11 | DNS: A yozuv | Eskiz panel | ⬜ qoldi |
| 12 | Saytni HTTP orqali ko'tarish | server | ⬜ qoldi |
| 13 | Ma'lumot va media ko'chirish | lokal → server | ⬜ qoldi |
| 14 | HTTPS sertifikat | server | ⬜ qoldi |
| 15 | Sertifikat yangilash (cron) | server | ⬜ qoldi |
| 16 | Darsdan oldin serverni tozalash | server | ⬜ qoldi |

## Shu serverda topilgan uchta muammo

Oddiy qo'llanmada yo'q, chunki bular aynan shu serverning holati:

1. **80-port band.** Serverga apt orqali nginx o'rnatilgan va ishlab turibdi (standart "Welcome to nginx!" sahifasi, boshqa hech narsa sozlanmagan). Docker'dagi nginx bu portni ololmaydi. — 5-qadam.
2. **Disk 8 GB, bo'sh joy 3.9 GB.** Docker image'lari ~1.2 GB, ustiga build keshi va videolar. — 3 va 4-qadamlar.
3. **Swap yo'q, RAM 911 MB.** Image build qilishda xotira yetmasligi mumkin. — 6-qadam.

---

# 1-qadam. Elastic IP ✅

Bajarildi: `13.60.107.7` → `i-0aeda94c8d901de53`.

Tekshirish (🖥 lokal):

```bash
ssh -i ~/Downloads/django-key.pem ubuntu@13.60.107.7 'echo SSH ishladi'
```

---

# 2-qadam. Security Group: 80 va 443 portlar

**Qayerda:** AWS Console.

**Nega kerak:** Security Group — serverning oldidagi qo'riqchi. U faqat ruxsat berilgan portlarga kirishga yo'l qo'yadi. Hozir faqat 22-port (SSH) ochiq, shuning uchun siz serverga kira olasiz, lekin sayt ochilmaydi. Brauzer saytga 80 (HTTP) yoki 443 (HTTPS) port orqali murojaat qiladi. Ikkalasi ham kerak: 80 — sayt HTTPS'gacha ishlashi va Let's Encrypt domenni tekshirishi uchun, 443 — shifrlangan ulanish uchun.

> Bu qadam sertifikat olishdan **oldin** bajarilishi kerak. Certbot 80-portga "hammasini HTTPS'ga yo'naltir" degan qoida qo'yadi. Agar o'sha paytda 443 yopiq bo'lsa, sayt butunlay ochilmay qoladi.

1. EC2 → chap menyu **Network & Security → Security Groups**
2. `sg-0ce10a173903cff45` (`launch-wizard-1`) havolasini bosing
3. Pastda **Inbound rules** tab → **`Edit inbound rules`**
4. **`Add rule`** tugmasini bosing va to'ldiring:

| Type | Source |
|---|---|
| HTTP | Anywhere-IPv4 |

5. Yana **`Add rule`**:

| Type | Source |
|---|---|
| HTTPS | Anywhere-IPv4 |

6. **`Save rules`**

`Type` ro'yxatidan `HTTP` yoki `HTTPS` ni tanlasangiz, port va protokol o'zi to'ladi.

> **Mavjud SSH qatorini tahrirlamang.** Uni o'zgartirsangiz serverga kira olmay qolasiz. Har bir yangi qoida uchun albatta `Add rule` bosing.

**Kutilgan natija:** ro'yxatda uchta qoida — SSH 22, HTTP 80, HTTPS 443.

---

# 3-qadam. Disk hajmini 30 GB ga oshirish

**Qayerda:** AWS Console.

**Nega kerak:** hozir diskda 3.9 GB bo'sh joy bor. Docker'ning o'zi ~400 MB, image'lar ~1.2 GB (Python 348 MB, PostgreSQL 425 MB, certbot 287 MB, nginx 102 MB), ustiga build keshi va o'quvchilar yuklaydigan video hamda taqdimotlar qo'shiladi. Disk to'lib qolsa, Docker ham, PostgreSQL ham to'xtaydi va sayt ishlamay qoladi. 30 GB bir necha yilga yetadi.

1. EC2 → chap menyu **Elastic Block Store → Volumes**
2. `django` instance'iga ulangan volume'ni belgilang (`Attached resources` ustunida instance ID ko'rinadi)
3. **`Actions`** → **`Modify volume`**
4. `Size` maydoniga `8` o'rniga **`30`** yozing
5. **`Modify`** → tasdiqlash oynasida yana **`Modify`**

**Kutilgan natija:** volume holati `Optimizing`, keyin `In-use`. Bir-ikki daqiqa vaqt oladi.

> Disk hajmini faqat oshirish mumkin, kamaytirib bo'lmaydi.

---

# 4-qadam. Diskni serverda kengaytirish

**Qayerda:** ☁️ server. Avval 3-qadam tugagan bo'lishi kerak.

Serverga kiring:

```bash
ssh -i ~/Downloads/django-key.pem ubuntu@13.60.107.7
```

Hozirgi holatni ko'ring:

```bash
df -h / && lsblk
```

AWS disk hajmini oshirdi, lekin Linux buni o'zi ishlatmaydi: avval bo'limni (partition), keyin fayl tizimini kengaytirish kerak.

Bo'limni kengaytirish:

```bash
sudo growpart /dev/nvme0n1 1
```

Fayl tizimini kengaytirish:

```bash
sudo resize2fs /dev/nvme0n1p1
```

**Tekshirish:**

```bash
df -h /
```

**Kutilgan natija:** `Size` ustunida ~29 GB.

---

# 5-qadam. Serverdagi eski nginx'ni o'chirish

**Qayerda:** ☁️ server.

Hozir 80-portni serverga o'rnatilgan nginx egallab turibdi. Docker'dagi nginx konteyneri ishga tusha olmaydi.

Kim band qilganini ko'rish:

```bash
sudo ss -tlnp | grep ":80 "
```

Nginx'ni to'xtatib, avtomatik ishga tushishini ham o'chirish:

```bash
sudo systemctl disable --now nginx
```

**Tekshirish — hech narsa chiqmasligi kerak:**

```bash
sudo ss -tlnp | grep ":80 "
```

> Nginx paketi o'z joyida qoladi, faqat ishlamaydi. Butunlay o'chirmoqchi bo'lsangiz: `sudo apt-get purge -y nginx nginx-common`

---

# 6-qadam. Swap qo'shish

**Qayerda:** ☁️ server.

RAM 911 MB. Image build qilishda xotira yetmay jarayon o'lib qolishi mumkin. 2 GB swap buni oldini oladi.

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

**Tekshirish:**

```bash
free -h
```

**Kutilgan natija:** `Swap` qatorida `2.0Gi`.

---

# 7-qadam. Docker o'rnatish

**Qayerda:** ☁️ server.

Ubuntu'ning o'z omborida Docker eski va `docker compose` plagini yo'q. Rasmiy omborni qo'shamiz.

Kerakli paketlar:

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl
```

Docker'ning GPG kaliti:

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

Docker'ni o'rnatish:

```bash
sudo apt-get update
```

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

`sudo` yozmaslik uchun foydalanuvchini `docker` guruhiga qo'shish:

```bash
sudo usermod -aG docker ubuntu
```

**Guruh faqat yangi sessiyada kuchga kiradi.** Serverdan chiqing:

```bash
exit
```

Qayta kiring:

```bash
ssh -i ~/Downloads/django-key.pem ubuntu@13.60.107.7
```

**Tekshirish:**

```bash
docker --version && docker compose version && docker run --rm hello-world
```

**Kutilgan natija:** versiyalar chiqadi va `Hello from Docker!` xabari ko'rinadi.

---

# 8-qadam. Lokalda Docker'da sinash

**Qayerda:** 🖥 lokal (Mac).

**Nega kerak:** Docker'ning asosiy foydasi shu — bir joyda ishlagan narsa boshqa joyda ham xuddi shunday ishlaydi. Shuning uchun avval kompyuterda sinaymiz: xato bo'lsa uni serverda emas, shu yerda topamiz. Serverda xatoni tuzatish uzoqroq: SSH, `git push`, `git pull`, qayta build. O'quvchilar uchun ham shu tartib qulay — ular Docker'ni serverga chiqmasdan, o'z laptopida ko'radi.

Serverdagi buyruqlar bilan lokal buyruqlar **bir xil**. Farqi faqat `.env` faylida: lokalda `DEBUG=True` va parollar oddiy, serverda `DEBUG=False` va parollar tasodifiy.

To'liq izohlari `DOCKER-DEPLOY.md` ning 3-bo'limida.

```bash
cd ~/PycharmProjects/LMS-U12 && docker --version && docker compose version
```

`.env` ga baza parolini qo'shish (`runserver` ga ta'sir qilmaydi, u avvalgidek SQLite bilan ishlaydi):

```bash
printf '\nDB_PASSWORD=lokal-sinov-paroli\n' >> ~/PycharmProjects/LMS-U12/.env
```

Sozlamalar to'g'ri o'qilayotganini tekshirish:

```bash
cd ~/PycharmProjects/LMS-U12 && docker compose config --quiet && echo "compose fayli to'g'ri"
```

Build qilib ishga tushirish (bitta buyruq):

```bash
cd ~/PycharmProjects/LMS-U12 && docker compose up -d --build && docker compose ps
```

Migratsiya va `collectstatic` ni alohida chaqirish shart emas — ularni konteyner ichida `entrypoint.sh` bajaradi. Buni loglarda ko'rish mumkin:

```bash
cd ~/PycharmProjects/LMS-U12 && docker compose logs web | head -20
```

Ma'lumotlarni yuklash:

```bash
cd ~/PycharmProjects/LMS-U12 && docker compose exec -T web python manage.py loaddata --format=json - < data.json
```

Media fayllarni ko'chirish:

```bash
cd ~/PycharmProjects/LMS-U12 && docker compose cp media/. web:/app/media/ && docker compose exec -u root web chown -R app:app /app/media
```

**Tekshirish:** brauzerda **http://localhost** oching, o'z hisobingiz bilan kiring, kurslar va rasmlar ko'rinishi kerak.

Sinov tugagach to'xtatish (ma'lumotlar saqlanadi):

```bash
cd ~/PycharmProjects/LMS-U12 && docker compose down
```

---

# 9-qadam. Kodni GitHub'ga push qilish

**Qayerda:** 🖥 lokal. Git buyruqlarini o'zingiz bajarasiz.

Server kodni GitHub'dan `git clone` bilan oladi, shuning uchun yangi fayllar repoda bo'lishi shart:

| Fayl | Holati |
|---|---|
| `Dockerfile` | yangi |
| `entrypoint.sh` | yangi |
| `.dockerignore` | yangi |
| `compose.yaml` | yangi |
| `nginx/http.conf` | yangi |
| `nginx/https.conf` | yangi |
| `DOCKER-DEPLOY.md` | yangi |
| `SERVER.md` | yangi (shu fayl) |
| `requirements.txt` | o'zgardi |
| `config/settings.py` | o'zgardi |
| `accounts/signals.py` | o'zgardi |

**Tekshirish (push'dan keyin):**

```bash
cd ~/PycharmProjects/LMS-U12 && git ls-remote origin main && git log --oneline -1
```

Ikkalasida bir xil hash bo'lishi kerak.

---

# 10-qadam. Kodni serverga klonlash va `.env` yaratish

**Qayerda:** ☁️ server.

**Nega `/srv/lms-u12`:** Linux'da `/srv` papkasi aynan shu server ko'rsatadigan ma'lumotlar uchun ajratilgan. Kodni `/home/ubuntu` ichida saqlash ham mumkin, lekin `/srv` da u foydalanuvchiga emas, serverga tegishli bo'lib turadi.

**Nega `.env` serverda yaratiladi:** maxfiy qiymatlar (kalit va parol) git'ga tushmaydi va kompyuterdan serverga umuman yuborilmaydi. Ular shu yerda generatsiya qilinadi va shu yerda qoladi. Har bir serverning o'z `.env` fayli bo'ladi.

Papka yaratish:

```bash
sudo mkdir -p /srv/lms-u12 && sudo chown ubuntu:ubuntu /srv/lms-u12
```

Klonlash:

```bash
git clone https://github.com/temuralidavron/LMS-U12.git /srv/lms-u12
```

**Tekshirish — `Dockerfile`, `compose.yaml`, `nginx` ko'rinishi kerak:**

```bash
ls /srv/lms-u12
```

`.env` faylini yaratish. Maxfiy kalit va baza paroli serverning o'zida generatsiya qilinadi:

```bash
cd /srv/lms-u12 && printf 'DEBUG=False\nSECRET_KEY=%s\nALLOWED_HOSTS=13.60.107.7,localhost,127.0.0.1\nCSRF_TRUSTED_ORIGINS=\nUSE_HTTPS=False\nSECURE_HSTS_SECONDS=3600\nDB_NAME=test_db\nDB_USER=test_db_user\nDB_PASSWORD=%s\nNGINX_CONF=http\n' "$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')" "$(openssl rand -hex 24)" > .env
```

Faylni himoyalash:

```bash
chmod 600 /srv/lms-u12/.env
```

**Tekshirish:**

```bash
cat /srv/lms-u12/.env
```

```bash
cd /srv/lms-u12 && docker compose config --quiet && echo "compose fayli to'g'ri"
```

---

# 11-qadam. DNS: A yozuv

**Qayerda:** Eskiz paneli (`my.eskiz.uz` → DNS yozuvlar → `new-project.uz`).

**Tavsiya: ikkita yozuv qo'shing** — bittasi sinov uchun, bittasi dars uchun:

| Maqsad | Name | Type | Record | TTL |
|---|---|---|---|---|
| Sinov (bugun) | `test` | `A` | `13.60.107.7` | `300` |
| Dars kuni | `docker` | `A` | `13.60.107.7` | `300` |

**Nega ikkita?** HTTPS yoqilgach, brauzer shu domenni "faqat HTTPS orqali ochiladi" deb eslab qoladi (HSTS). Sinovda ishlatilgan domen bilan darsda HTTP bosqichini ko'rsatmoqchi bo'lsangiz, brauzer saytni ochmay qo'yadi. Ikki domen bilan bu muammo umuman chiqmaydi. Let's Encrypt sertifikat limiti ham har bir domen uchun alohida hisoblanadi.

Mavjud yozuvlarga tegmang: `alisher.new-project.uz` eski serveringizga, `www` va `new-project.uz` boshqa xostingga qarab turibdi.

**Tekshirish (🖥 lokal, 5-30 daqiqadan keyin):**

```bash
dig +short test.new-project.uz
```

**Kutilgan natija:** `13.60.107.7`. Boshqa natija chiqsa yoki bo'sh bo'lsa — hali tarqalmagan, kuting.

---

# 12-qadam. Saytni HTTP orqali ko'tarish

**Qayerda:** ☁️ server. Izohlari `DOCKER-DEPLOY.md` 8-bo'limida.

**Bitta buyruq ichida nimalar bo'ladi:**

| Tartib | Nima bo'ladi | Kim qiladi |
|---|---|---|
| 1 | `web` image'i quriladi | `--build` |
| 2 | `db` ko'tariladi va `healthy` bo'lishi kutiladi | `compose.yaml` dagi `depends_on` |
| 3 | migratsiyalar qo'llanadi | `entrypoint.sh` |
| 4 | static fayllar yig'iladi | `entrypoint.sh` |
| 5 | gunicorn ishga tushadi | Dockerfile'dagi `CMD` |
| 6 | nginx ko'tariladi | `compose.yaml` |

Build qilib ishga tushirish (birinchi marta 2-4 daqiqa):

```bash
cd /srv/lms-u12 && docker compose up -d --build
```

Nima bo'lganini ko'rish:

```bash
cd /srv/lms-u12 && docker compose logs web | head -20
```

`==> Migratsiyalar qo'llanmoqda`, migratsiya qatorlari, `==> Static fayllar yig'ilmoqda` va gunicorn'ning `Listening at: http://0.0.0.0:8000` qatori chiqishi kerak.

**Tekshirish:**

```bash
cd /srv/lms-u12 && docker compose ps
```

`db` — `healthy`, `web` va `nginx` — `Up`. Faqat nginx qatorida portlar ko'rinadi.

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1/accounts/login/
```

🖥 LOKAL:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://13.60.107.7/accounts/login/
```

**Kutilgan natija:** ikkalasi ham `200`. Brauzerda: **http://13.60.107.7**

Xato bo'lsa, loglar:

```bash
cd /srv/lms-u12 && docker compose logs web | tail -30
```

---

# 13-qadam. Ma'lumot va media fayllarni ko'chirish

**Qayerda:** 🖥 lokal → ☁️ server.

**Nega kerak:** lokalda ma'lumot SQLite faylida, serverda esa PostgreSQL'da. Fayl nusxasini ko'chirib bo'lmaydi, shuning uchun ma'lumot `data.json` orqali o'tkaziladi: `dumpdata` uni SQLite'dan o'qiydi, `loaddata` PostgreSQL'ga yozadi. Media fayllar git'da yo'q (`.gitignore` da), shuning uchun ular alohida yuboriladi.

**Nega `chown` kerak:** fayllar konteynerga ko'chirilganda ularning egasi kompyuteringizdagi foydalanuvchi bo'lib qoladi. Konteyner ichida Django `app` nomidan ishlaydi va begona egalikdagi papkaga yangi fayl yoza olmaydi. `chown` buni to'g'rilaydi, aks holda o'quvchi fayl yuklaganda `Permission denied` chiqadi.

**Nega `data.json` o'chiriladi:** faylda foydalanuvchilarning parol hash'lari bor. Bazaga yuklangandan keyin uning serverda yotishi keraksiz xavf.

Fayllarni yuborish (🖥 lokal):

```bash
cd ~/PycharmProjects/LMS-U12 && scp -i ~/Downloads/django-key.pem data.json ubuntu@13.60.107.7:~/
```

```bash
cd ~/PycharmProjects/LMS-U12 && scp -i ~/Downloads/django-key.pem -r media ubuntu@13.60.107.7:~/
```

Ma'lumotni bazaga yuklash (☁️ server):

```bash
cd /srv/lms-u12 && docker compose exec -T web python manage.py loaddata --format=json - < ~/data.json
```

**Kutilgan natija:** `Installed 81 object(s) from 1 fixture(s)`

Media fayllarni volume'ga ko'chirish va egasini to'g'rilash:

```bash
cd /srv/lms-u12 && docker compose cp ~/media/. web:/app/media/
```

```bash
cd /srv/lms-u12 && docker compose exec -u root web chown -R app:app /app/media
```

**Tekshirish — hamma qatorda `app app` bo'lishi kerak:**

```bash
cd /srv/lms-u12 && docker compose exec web ls -la /app/media /app/media/courses
```

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://13.60.107.7/media/courses/1000074614.jpg
```

Parollar bor faylni o'chirish:

```bash
rm ~/data.json
```

Superuserlarning rolini `admin` ga qo'yish:

```bash
cd /srv/lms-u12 && docker compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); print('updated', U.objects.filter(is_superuser=True).update(role='admin'))"
```

---

# 14-qadam. HTTPS sertifikat

**Qayerda:** ☁️ server. To'liq izohlari `DOCKER-DEPLOY.md` 10-bo'limida.

Shartlar: 2-qadam (443-port ochiq) va 11-qadam (DNS) tayyor bo'lishi kerak.

**Nega bu tartib:**
1. **Domen avval Django'ga tanitiladi.** Django faqat `ALLOWED_HOSTS` dagi domenlarga javob beradi. Domen qo'shilmasa, `400 Bad Request` chiqadi va certbot tekshiruvi ham o'tmaydi.
2. **Sertifikat faqat domenga beriladi.** IP manzilga (`13.60.107.7`) Let's Encrypt sertifikat bermaydi. Shuning uchun DNS yozuvi shart.
3. **Avval test (`--staging`) sertifikati.** Let's Encrypt bir hafta ichida bitta domenga beriladigan sertifikat sonini cheklaydi. Sozlamada xato bo'lsa, urinishlar limitni yeb qo'yadi va bir hafta kutishga to'g'ri keladi. Test serverida limit yo'q.
4. **Keyin nginx va Django HTTPS'ga o'tkaziladi.** Sertifikat olinmasdan turib `NGINX_CONF=https` qilinsa, nginx "cannot load certificate" deb ishga tushmaydi.

🖥 LOKAL — tekshirish:

```bash
dig +short test.new-project.uz
```

```bash
nc -z -G 10 13.60.107.7 443 && echo "443 OCHIQ" || echo "443 YOPIQ"
```

Domenni Django'ga tanitish (☁️ server):

```bash
cd /srv/lms-u12 && sed -i 's|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=test.new-project.uz,13.60.107.7,localhost,127.0.0.1|' .env
```

```bash
cd /srv/lms-u12 && docker compose up -d web
```

**Tekshirish — `200` bo'lishi kerak:**

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://test.new-project.uz/accounts/login/
```

Avval test sertifikati (Let's Encrypt limitini sarflamaydi). `EMAIL` o'rniga o'z manzilingizni yozing:

```bash
cd /srv/lms-u12 && docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d test.new-project.uz --cert-name lms --email EMAIL --agree-tos --no-eff-email --staging
```

`Successfully received certificate` chiqsa, test sertifikatini o'chirib, haqiqiysini olamiz:

```bash
cd /srv/lms-u12 && docker compose run --rm certbot delete --cert-name lms
```

```bash
cd /srv/lms-u12 && docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d test.new-project.uz --cert-name lms --email EMAIL --agree-tos --no-eff-email
```

Nginx va Django'ni HTTPS'ga o'tkazish:

```bash
cd /srv/lms-u12 && sed -i -e 's|^NGINX_CONF=.*|NGINX_CONF=https|' -e 's|^USE_HTTPS=.*|USE_HTTPS=True|' -e 's|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=https://test.new-project.uz|' .env
```

```bash
cd /srv/lms-u12 && docker compose up -d
```

**Tekshirish (🖥 lokal):**

```bash
curl -sI http://test.new-project.uz/accounts/login/ | head -3
```

`301` va `Location: https://...` bo'lishi kerak.

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://test.new-project.uz/accounts/login/
```

`200` bo'lishi kerak. Brauzerda qulf belgisi ko'rinadi.

```bash
cd /srv/lms-u12 && docker compose exec web python manage.py check --deploy
```

Faqat `security.W021` ogohlantirishi qolishi kerak.

---

# 15-qadam. Sertifikatni avtomatik yangilash

**Qayerda:** ☁️ server.

**Nega kerak:** Let's Encrypt sertifikati cheklangan muddat amal qiladi (hozir 90 kun). Muddati o'tsa, brauzer saytni "xavfli" deb ko'rsatadi. Cron har kuni `certbot renew` ni chaqiradi: muddat yaqin bo'lmasa u hech narsa qilmaydi, yaqin bo'lsa sertifikatni yangilaydi.

**Nega oxirida `nginx -s reload`:** certbot yangi sertifikat faylini yozadi, lekin ishlab turgan nginx eskisini xotirasida saqlab turadi. `reload` uni saytni to'xtatmasdan qayta o'qishga majbur qiladi.

Sinab ko'rish:

```bash
cd /srv/lms-u12 && docker compose run --rm certbot renew --dry-run
```

Kunlik vazifa:

```bash
(crontab -l 2>/dev/null; echo '0 3 * * * cd /srv/lms-u12 && /usr/bin/docker compose run --rm certbot renew --quiet && /usr/bin/docker compose exec -T nginx nginx -s reload') | crontab -
```

**Tekshirish:**

```bash
crontab -l
```

---

# 16-qadam. Darsdan oldin serverni tozalash

**Qayerda:** ☁️ server. Darsda hamma narsani noldan ko'rsatish uchun.

Konteynerlar, volume'lar va tarmoqni o'chirish:

```bash
cd /srv/lms-u12 && docker compose --profile tools down -v
```

Image'lar va build keshini o'chirish:

```bash
docker system prune -a -f
```

Loyiha papkasini o'chirish:

```bash
sudo rm -rf /srv/lms-u12
```

Cron vazifasini o'chirish:

```bash
crontab -r
```

Docker'ning o'zini ham o'chirish (darsda o'rnatishni ko'rsatmoqchi bo'lsangiz):

```bash
sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```bash
sudo rm -rf /var/lib/docker /var/lib/containerd /etc/apt/sources.list.d/docker.list
```

**Tekshirish:**

```bash
docker --version 2>&1 | head -1; ls /srv; df -h /
```

> Swap (`/swapfile`), Elastic IP, Security Group va disk hajmi joyida qoladi — ularni qayta sozlash shart emas.
>
> Darsda `docker.new-project.uz` domenidan foydalaning. Sinovda ishlatilgan `test.new-project.uz` brauzerlarda HSTS bilan eslab qolingan bo'ladi va HTTP bosqichini ko'rsatishga xalaqit beradi.
