# Our Little World ♡

เว็บบันทึกความทรงจำส่วนตัวสำหรับคู่รัก: Django + PostgreSQL + Private S3 + OpenAI (optional)

## สิ่งที่ทำได้
- หน้าแรก, ความทรงจำพร้อมภาพและสถานที่, โน้ตส่วนตัว/โน้ตแชร์, สิ่งที่ชอบ, ตารางเรียนของแต่ละคน, หน้าเราสองคน
- ธีมครีมชมพู, Dark Mode, รองรับมือถือ, เมนูด้านล่าง
- เก็บเนื้อหาในฐานข้อมูล PostgreSQL, เก็บรูปใน S3 แบบ private, ลิงก์รูปหมดอายุ
- อ่านภาพตารางเรียนด้วย AI และให้ยืนยันก่อนเพิ่ม
- ตรวจ revision เพื่อเตือนเมื่อแก้ไขจากคนละอุปกรณ์
- ปิด public registration (สร้างบัญชีผ่าน Django admin)

## Start (Docker)
1. Copy .env.example to .env
2. Set DJANGO_SECRET_KEY and credentials for private S3 bucket. Without S3 configuration, images are written to local media/ during development only (not persistent in containers).
3. docker compose up --build -d
4. docker compose exec web python manage.py migrate
5. docker compose exec web python manage.py createsuperuser
6. Open http://localhost:8000 ; log in, create the partner account at /admin/ (Users > Add). Keep only the intended accounts.
7. Optional: set OPENAI_API_KEY in .env, restart service to enable AI extraction.

## Production
Set DJANGO_DEBUG=0, trusted HTTPS domain, valid secret, real managed PostgreSQL DATABASE_URL, private S3 settings, HTTPS reverse proxy, backups, and secret manager. Run migrate for each deployment. Do not use the development PostgreSQL password in production. GitHub Pages cannot serve this dynamic app. Upload photos only after securing deployment.

## Limitations
AI cannot guarantee accurate OCR; always confirm results. Editing individual photo captions and delete-per-photo, accounts invitation flow, calendar import and realtime push alerts are not yet implemented. Django admin still has normal superuser privileges. Do not create additional untrusted admin/staff accounts.

## Stack
Python 3.12, Django 5.2, PostgreSQL 16, Pillow, Boto3, django-storages, OpenAI API, Gunicorn.
