# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

## Authentication integration

The app protects `/send`, `/wallet`, `/history`, `/track`, `/profile`, and `/withdraw` in the browser. Visitors who are not signed in are redirected to `/login` and returned to the page they originally requested after successful authentication.

The sign-in and registration forms call `POST /api/auth/login/` and `POST /api/auth/register/`. A successful sign-in response should include a bearer token (`accessToken`, `access_token`, `access`, or `token`), a refresh token (`refresh`), and a `user` object. Protected requests send the bearer token when one is returned and always include cookies. Logout calls `POST /api/auth/logout/` and blacklists the refresh token.

Route guards only protect the client experience; the API must independently validate the session/token and authorize every operation and resource ownership. In particular, `/api/withdrawals/` must reject unauthenticated or unauthorized requests on the server.

## Django API

The Django API lives in [`backend/`](backend/). It exposes JWT-authenticated auth and withdrawal endpoints, including user-scoped withdrawal reads. Run it locally with a separate virtual environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Run those commands from `backend/`, then start the Vite app normally. Vite proxies `/api` to `http://127.0.0.1:8000` in development. For a separately deployed API, set `VITE_API_BASE_URL` to its origin and set Django's `CORS_ALLOWED_ORIGINS`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_ENV=production`, and `DJANGO_SECRET_KEY` to production values. A production server refuses to start without `DJANGO_SECRET_KEY`; see [`backend/.env.example`](backend/.env.example).

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh
