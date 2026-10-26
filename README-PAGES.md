# GitHub Pages + Django backend

The site is built automatically from `site/` by `.github/workflows/pages.yml`.

1. GitHub repository > Settings > Pages > Build and deployment > Source > **GitHub Actions**.
2. GitHub repository > Settings > Secrets and variables > Actions > Variables > New repository variable: `API_BASE_URL` = `https://YOUR-BACKEND.example.com`.
3. Deploy the Django app separately (Render/Railway/etc.), run `python manage.py migrate`, create 2 users in Django Admin. Set `CORS_ALLOWED_ORIGINS=https://pakk49.github.io`, `DJANGO_ALLOWED_HOSTS=YOUR-BACKEND.example.com`, `DJANGO_DEBUG=0`, strong Django secret, managed `DATABASE_URL`, and private `S3_*` credentials.
4. Trigger `Deploy Our Little World to GitHub Pages` from Actions > Run workflow. Visit `https://pakk49.github.io/Our-Little-World/`.
5. Check login, memory upload, private photo, notes, schedule and AI with both test accounts.

**GitHub Pages alone is not a working backend.** API login tokens are held in tab-scoped sessionStorage (cleared on tab close). Protect the backend with HTTPS. Do not put credentials in GitHub variables used by the frontend. Repo visibility and Pages availability depend on plan and settings. Until API_BASE_URL is configured, Pages shows a setup/preview state rather than claiming login works.

Backend APIs:
- POST /api/login/ returns Token; POST /api/logout/ revokes it
- GET /api/me/
- GET/POST /api/memories/, PUT/DELETE /api/memories/<id>/
- GET/POST /api/notes/, PUT/DELETE /api/notes/<id>/
- GET/POST /api/lessons/, PUT/DELETE /api/lessons/<id>/
- GET /api/photos/<id>/ uses authentication
- POST /api/scan/ and POST /api/scan/confirm/

All secured endpoints use `Authorization: Token <token>`. The couple access model currently relies on creating only intended users in Django Admin; it is **not** yet a full workspace invite system.
