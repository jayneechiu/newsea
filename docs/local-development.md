# Local development

Newsea has a mock-first frontend workflow so UI work does not depend on Azure,
PostgreSQL, Reddit, or OpenAI.

## Fastest path: mock feed

Use Node.js 22.18+; CI and Pages use Node 22.

```bash
cd ui
npm ci
npm run dev:mock
```

Open <http://localhost:3000>. Mock mode reads the structured cards in
`ui/src/data/demo-cards.json`. The UI displays a `Preview data` badge so sample
content is never confused with a live trend.

## Live API mode

Start the API from the repository root:

```bash
INIT_IN_BACKGROUND=true python3 -m uvicorn backend.api.main:app --reload --port 8000
```

Then start the frontend in another terminal:

```bash
cd ui
npm run dev
```

The Vite development server proxies `/api` to `http://localhost:8000`. If the
feed endpoint is unavailable or returns no cards, the frontend automatically
uses the local demo cards and marks them as preview data.

## Accounts (sign up / log in)

In live API mode, `/login` creates real accounts. The mock and demo builds keep
the simulated login.

- **Sign up:** email + password (at least 8 characters). Success signs you in.
- **Entry points:** every page header has a "Log in / Sign up" button. On the
  home page, guests see a one-time welcome dialog after 3 seconds. In it they
  can pick interests, then create an account or log in (closing it keeps them
  browsing as a guest). To show it again, delete `newsea:welcome-seen` from localStorage.
  Pages that need login redirect to `/login?next=…`, which returns the user to
  the same page after login.
- **Log in / log out:** the API sets an httpOnly `newsea_session` cookie (30
  days); logging out deletes the session server-side.
- **Endpoints:** `POST /api/auth/register`, `POST /api/auth/login`,
  `POST /api/auth/logout`, `GET /api/me`.
- Tables (`users.password_hash`, `user_sessions`, `user_interactions`) are
  created automatically when the API connects to PostgreSQL.
- Set `SESSION_COOKIE_SECURE=true` in the backend environment when serving
  over HTTPS.

If the API logs a PostgreSQL connection timeout, the database firewall is
probably blocking your current public IP. On Azure, add it under the server's
**Networking → Firewall rules**.

## Checks before publishing

```bash
cd ui
npm run typecheck
npm run build
npm run preview
```

The production preview is available at <http://localhost:4173> by default.

## Environment modes

- `.env.mock` enables the dependency-free mock feed.
- `.env` contains the developer's normal API base URL and is ignored by Git.
- `.env.example` documents safe frontend variables. Never place Reddit,
  OpenAI, database, or SMTP secrets in a `VITE_` variable because Vite exposes
  those values to the browser bundle.

## Newsletter subpage

The preserved newsletter experience is available at
<http://localhost:3000/newsletter>. Public and mock builds render a digest
preview without exposing an email-send action.

To show the connected owner controls locally, add this to `ui/.env`:

```env
VITE_ENABLE_NEWSLETTER_SEND=true
```

Only enable this in a trusted local environment. The control asks for the
server-side admin key before it can start a send.

Render the current email template without sending:

```bash
python3 scripts/send_test_newsletter.py --render-only
```

Send a real test email to the recipients configured in the root `.env`:

```bash
python3 scripts/send_test_newsletter.py --limit 4
```

### Real Reddit preview (safe by default)

With Reddit credentials in the root `.env`, fetch live posts and render the
current email without sending it:

```bash
python3 scripts/render_live_newsletter.py --subreddit todayilearned --limit 4
open /tmp/newsea-live-newsletter.html
```

GPT-written summaries, humorous hooks, and editor words are enabled by default,
matching the connected newsletter pipeline. The command also saves
`/tmp/newsea-live-newsletter.json`; reuse that exact edition without Reddit or
OpenAI calls:

```bash
python3 scripts/render_live_newsletter.py --from-package /tmp/newsea-live-newsletter.json
python3 scripts/send_test_newsletter.py --package-file /tmp/newsea-live-newsletter.json
```

Use `--without-ai` only for an offline fallback. Fallback hooks remain specific
to each title. The render command never sends email.

### Subscriber approval

Set a long random `NEWSLETTER_ADMIN_KEY` in the backend environment. Public
applications submitted on `/newsletter` are always stored as `pending` and
inactive. Review them at `/newsletter/admin`; the key remains in page memory
and is sent only as the `X-Newsea-Admin-Key` request header.

Campaign sends require the same key and resolve recipients only from approved,
active database rows. `EMAIL_RECIPIENTS` remains available for the explicit
local test script above, but the production campaign endpoint does not use it.
