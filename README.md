# Newsea

**The best of Reddit, made instantly useful.**

Newsea turns high-signal Reddit conversations into a visual, continuously
scrollable feed. Instead of sending people through clickbait headlines and long
threads, each card delivers the useful conclusion first, then expands in place
to reveal the strongest takeaways and original communities.

> See what everyone—and everyone unlike you—is talking about.

Newsea is currently a non-commercial portfolio project and product prototype.

## Why Newsea

Recommendation systems are very good at showing people more of what they
already like. They are less useful for answering:

- What is everyone paying attention to right now?
- What is changing in my city?
- What does a community outside my normal feed know that I do not?
- Which parts of a long discussion are actually worth remembering?

Newsea explores a **human signal feed**: Reddit's existing community knowledge,
organized into concise visual cards rather than another publication,
newsletter, or social network waiting for creators.

## Product experience

The prototype has four permanent views:

- **For you** — content shaped by user interests without removing discovery.
- **Everyone** — the strongest signals across communities.
- **Dallas** — a local trend and recommendation lens.
- **Other worlds** — useful views into communities outside the user's routine.

Every content card contains:

1. A complete, useful headline—not a teaser.
2. Context explaining why the signal matters.
3. Community and source evidence.
4. Three expandable takeaways.
5. Links to the original Reddit communities.

Cards can be saved or hidden locally. The responsive layout uses four columns
on large screens and a focused single-column feed on mobile.

The original newsletter remains available at `/newsletter` as a slower weekly
digest built from the same ContentCards. Public builds show a safe preview;
connected email controls are opt-in for the project owner. Every public signup
is stored as a pending request; `/newsletter/admin` lets the owner approve or
reject it before that address can receive a campaign.

## Run the visual prototype

The fastest way to use Newsea does not require PostgreSQL, Reddit, OpenAI, or
Azure:

```bash
git clone https://github.com/jayneechiu/newsea.git
cd newsea/ui
npm install
npm run dev:mock
```

Open [http://localhost:3000](http://localhost:3000).

Mock mode reads structured sample cards from
`ui/src/data/demo-cards.json`. The interface displays a **Preview data** badge
so sample content is never presented as a live trend.

### Frontend checks

```bash
cd ui
npm run typecheck
npm run build
npm run preview
```

The production preview runs at
[http://localhost:4173](http://localhost:4173) by default.

Render or send the matching email design with local preview cards:

```bash
python3 scripts/send_test_newsletter.py --render-only
python3 scripts/send_test_newsletter.py --limit 4
```

The send command uses the SMTP account and recipients configured in the root
`.env`.

To preview the same template with current Reddit data without sending email:

```bash
python3 scripts/render_live_newsletter.py --subreddit todayilearned --limit 4
```

This creates both HTML and a reusable JSON content package. GPT summaries,
individual humorous hooks, and editor words are generated once; preview and
send reuse the same package rather than fetching or rewriting the edition.

## Live API development

The repository also contains the original Reddit ingestion and newsletter
backend. It provides a foundation for the next live-feed phase:

- Reddit access through PRAW.
- Post and top-comment collection.
- OpenAI-powered summaries.
- PostgreSQL persistence.
- FastAPI endpoints.
- Docker-based backend packaging.

Requirements:

- Python 3.11+
- PostgreSQL
- Reddit API credentials
- An OpenAI API key for AI enrichment

Create an environment and install the backend:

```bash
cd newsea
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r backend/api/requirements.txt
```

Copy and configure the environment file:

```bash
cp .env.example .env
```

Start the API:

```bash
INIT_IN_BACKGROUND=true \
python -m uvicorn backend.api.main:app --reload --port 8000
```

API documentation is available at
[http://localhost:8000/docs](http://localhost:8000/docs).

Start the frontend in live mode from another terminal:

```bash
cd ui
npm run dev
```

The frontend requests `/api/feed`. Until the new feed endpoint is connected to
the database, an unavailable or empty response automatically falls back to the
local preview cards instead of showing an empty page.

See [Local development](docs/local-development.md) for environment modes and
additional commands.

## ContentCard contract

The frontend is built around a structured `ContentCard`, not a raw Reddit post
or free-form AI summary:

```json
{
  "id": "dallas-bbq",
  "lane": ["everyone", "dallas"],
  "cardType": "local-trend",
  "theme": "coral",
  "eyebrow": "Dallas local obsession",
  "headline": "Korean–Texas BBQ is the order Dallas keeps repeating",
  "context": "Local food threads keep converging on the same dishes.",
  "takeaways": [
    "The first useful takeaway",
    "The strongest community consensus",
    "What people already think is overhyped"
  ],
  "topics": ["food", "local", "dallas"],
  "audience": "Dallas food communities",
  "sourceCount": 18,
  "communityCount": 6,
  "trendLabel": "Rising this week",
  "sources": []
}
```

This contract lets the UI remain stable while content generation evolves from
curated fixtures to a real ingestion, ranking, and enrichment pipeline.

## Architecture

```text
Current recruiter-safe path

demo-cards.json
      ↓
Feed service ──→ React visual feed ──→ save / hide / expand
      ↑
automatic fallback


Live pipeline in progress

Reddit API
    ↓
posts + comments
    ↓
metric snapshots and candidate scoring
    ↓
structured AI enrichment
    ↓
quality and safety checks
    ↓
PostgreSQL ContentCards
    ↓
FastAPI /api/feed
```

## Current status

### Working now

- Four-lane visual feed.
- Responsive masonry-style layout.
- Structured, type-safe content cards.
- Inline expansion with source links.
- Local save and hide interactions.
- Preserved Newsletter subpage with a recruiter-safe digest preview.
- Owner-gated newsletter applications and approved-recipient campaign sends.
- Dependency-free mock mode.
- Automatic fallback when the live feed is unavailable.
- Successful TypeScript and production build checks.

### Existing backend foundation

- Reddit post and comment fetching.
- GPT summary generation.
- PostgreSQL Schema V2.
- FastAPI service initialization and health endpoints.
- Backend Docker image and Azure Container Registry workflow.

### Next milestones

1. Add PostgreSQL Schema V3 tables for comments, metric snapshots,
   `content_cards`, card sources, and interaction events.
2. Generate schema-validated card JSON from posts and high-signal comments.
3. Implement `/api/feed` for Everyone, Dallas, Other worlds, and For you.
4. Add candidate quality, velocity, novelty, repetition, and safety scoring.
5. Deploy the frontend and backend behind a public recruiter-friendly URL.
6. Add smoke tests, monitoring, and a curated production fallback dataset.

## Repository structure

```text
newsea/
├── backend/
│   ├── api/                  # FastAPI service
│   └── scraper/              # Reddit, OpenAI, PostgreSQL, newsletter legacy
├── docs/
│   ├── database_schema_v2.md
│   └── local-development.md
├── templates/                # Legacy newsletter templates
├── tests/                    # Backend integration checks
├── ui/
│   ├── src/components/       # Feed UI and ContentCard
│   ├── src/data/             # Structured preview cards
│   ├── src/services/         # API and fallback feed services
│   ├── src/types/            # ContentCard data contract
│   └── src/pages/            # Application pages
└── docker-compose.yml
```

## Environment and data safety

- Never place Reddit, OpenAI, database, or SMTP credentials in a `VITE_`
  variable. Vite exposes those values to the browser bundle.
- Keep backend credentials in the root `.env`, which is ignored by Git.
- Preview cards are explicitly labeled and should not be interpreted as live
  measurements.
- Live Reddit content should retain attribution and source links, minimize
  stored user identity, and support removal when source content is deleted.
- Commercial use of Reddit data requires the appropriate Reddit approval and
  agreement. Newsea currently operates as a non-commercial portfolio project.

## Technology

- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Backend:** Python, FastAPI, PRAW
- **Data:** PostgreSQL
- **AI enrichment:** OpenAI API
- **Packaging:** Docker
- **Previous cloud setup:** Azure Container Registry and PostgreSQL

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This repository is available under the [MIT License](LICENSE).

Reddit content belongs to its respective authors and communities. Newsea is not
affiliated with or endorsed by Reddit.
