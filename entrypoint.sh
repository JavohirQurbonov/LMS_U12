#!/bin/sh
# =====================================================================
# entrypoint.sh — konteyner ishga tushganda BIRINCHI bajariladigan skript.
#
# Dockerfile'dagi ENTRYPOINT shu faylni chaqiradi. CMD dagi buyruq esa
# unga parametr bo'lib uzatiladi va skript oxirida ishga tushadi.
#
# Maqsadi: konteyner har ko'tarilganda ikki ish o'zi bajarilsin —
#   1. migratsiyalar qo'llansin (bazada jadvallar yaratilsin)
#   2. static fayllar yig'ilsin (nginx ularni bera olsin)
#
# Shuning uchun deploy bitta buyruqdan iborat bo'ladi:
#   docker compose up -d --build
#
# Bu qadamlarni qo'lda ham bajarish mumkin, masalan darsda ko'rsatish uchun:
#   docker compose exec web python manage.py migrate
# =====================================================================

# set -e — biror buyruq xato bersa, skript shu yerda to'xtaydi va
# gunicorn umuman ishga tushmaydi. Yarim ishlaydigan sayt o'rniga
# aniq xato loglarda ko'rinadi: docker compose logs web
set -e

# Quyidagi ikki qadam faqat asosiy server ishga tushayotganda kerak.
# "docker compose run --rm web python manage.py shell" kabi bir martalik
# buyruqlarda ular ortiqcha vaqt oladi, shuning uchun tekshiruv qo'yilgan.
if [ "$1" = "gunicorn" ]; then
    echo "==> Migratsiyalar qo'llanmoqda"
    python manage.py migrate --noinput

    echo "==> Static fayllar yig'ilmoqda"
    python manage.py collectstatic --noinput

    echo "==> Tayyor, gunicorn ishga tushmoqda"
fi

# exec — joriy jarayonni CMD dagi buyruq bilan almashtiradi.
# Shunda gunicorn konteynerning asosiy jarayoni (PID 1) bo'ladi va
# "docker compose stop" yuborgan to'xtash signalini to'g'ridan-to'g'ri oladi.
# "$@" — Dockerfile'dagi CMD qatori (gunicorn va uning parametrlari).
exec "$@"
