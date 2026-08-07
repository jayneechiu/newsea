# Reddit Newsletter Bot 🚀

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Reddit API](https://img.shields.io/badge/Reddit-API-orange.svg)](https://www.reddit.com/dev/api/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)](https://www.postgresql.org/)

An intelligent Reddit trending-post aggregator that automatically generates beautiful newsletters and sends them on a schedule. It integrates OpenAI GPT for content summarization and analysis and uses PostgreSQL for data storage.

## ✨ Key Features

- 🔥 **Trending Posts from Multiple Subreddits** - Supports custom subreddits and scraping rules
- 🤖 **AI-Powered Summaries** - GPT-powered post summaries and popularity analysis
- 📧 **Beautiful Email Templates** - Responsive HTML design with a plain-text version
- ⏰ **Automated Scheduled Delivery** - Configurable delivery times and frequency
- 💾 **PostgreSQL Database** - Reliable data storage with cloud deployment support
- 📊 **Statistics and Management** - Delivery success rates, content statistics, and more
- 🛠️ **Rich Toolset** - Practical tools for testing, management, cleanup, and more

## 🚀 Quick Start

### 1. Requirements

- Python 3.11+
- PostgreSQL database

### 2. Installation

```bash
git clone https://github.com/jayneechiu/newsea.git
cd newsea
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
# Or install the unified backend dependencies
pip install -r backend/api/requirements.txt
```

### 3. Configure the Database

**Option 1: Use Azure Database for PostgreSQL (Recommended)**

1. Create a PostgreSQL service in the [Azure Portal](https://portal.azure.com/)
2. Configure firewall rules to allow your IP address
3. Copy the database connection URL

**Option 2: Use a Local PostgreSQL Database**

```bash
# Windows (administrator privileges required)
.\install_postgresql.bat

# Or install it manually
choco install postgresql -y
```

### 4. Configure Environment Variables

Copy the configuration template:

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

Edit the `.env` file and enter your configuration details:

```env
# Reddit API configuration
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# PostgreSQL database configuration
DATABASE_URL=postgresql://username:password@host:port/database

# Email configuration
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient@example.com
```

### 5. Test and Run

```bash
# Test the database connection
python tests/test_postgres_connection.py

# Test the Reddit connection
python tests/test_reddit_connection.py

# Test email delivery
python tests/test_email_connection.py

# Run the scraper (safe connection check; does not send emails)
python backend/scraper/run_job.py --test

# Run the scraper (actual delivery/scheduling logic)
python backend/scraper/run_job.py
```

## ⚙️ Configuration

### Reddit API Configuration

1. Visit [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Create a new application (select the "script" type)
3. Add the relevant parameters to your `.env` file

### PostgreSQL Database Configuration

**Azure Database for PostgreSQL (Recommended):**

```env
DATABASE_URL=postgresql://username:password@your-server.postgres.database.azure.com:5432/postgres
```

**Local Database:**

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/reddit_newsletter
```

### OpenAI API Configuration

1. Get an [OpenAI API key](https://platform.openai.com/api-keys)
2. Set `OPENAI_API_KEY` in your `.env` file
3. Choose a GPT model (`gpt-4o-mini` is recommended)

### Email Service Configuration

Any SMTP email service is supported:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

## 🛠️ Development and Testing

```bash
# Run tests
python tests/test_postgres_connection.py  # PostgreSQL test
python tests/test_reddit_connection.py    # Reddit API test
python tests/test_email_connection.py     # Email delivery test
python tests/test_full_system.py          # Full system test

# Run the API service
uvicorn backend.api.main:app --reload --port 8000

# Run the scraper
python backend/scraper/run_job.py          # Scheduled/production run
python backend/scraper/run_job.py --test   # Connection check (does not send emails)
```

## 📁 Project Structure

```
├── backend/               # Backend (API + Scraper)
│   ├── api/
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── Dockerfile       # Unified backend image
│   │   └── requirements.txt # Backend dependencies (API + Scraper)
│   └── scraper/
│       ├── run_job.py
│       ├── config_manager.py
│       ├── reddit_scraper.py
│       ├── chatgpt_client.py
│       ├── newsletter_sender.py
│       └── database_manager.py
├── templates/             # Email templates
│   ├── newsletter_template.txt   # Plain-text template
│   └── newsletter_template2.html # HTML template
├── tests/                 # Test modules
│   ├── test_postgres_connection.py # PostgreSQL connection test
│   ├── test_reddit_connection.py   # Reddit API test
│   ├── test_email_connection.py    # Email functionality test
│   └── test_full_system.py         # Full system test
├── .github/               # CI/CD configuration
└── .env.example           # Environment variable configuration template
```

## 📊 Highlights

### AI-Powered Summaries

- Uses GPT to summarize and analyze each trending post
- Generates personalized editorial notes
- Intelligently identifies why a post is popular

### PostgreSQL Database

- Uses PostgreSQL for reliable data storage
- Supports cloud databases such as Azure Database for PostgreSQL and Supabase
- Provides complete data persistence and historical records
- Automatically initializes the database schema

### Flexible Configuration

- Supports scraping multiple subreddits simultaneously
- Configurable post limits and filtering criteria
- Flexible delivery time and frequency settings

## 🔧 Development

### Requirements

- Python 3.11+
- PostgreSQL database
- Internet connection (for API calls)

### Testing

```bash
# Test the database connection
python tests/test_postgres_connection.py

# Test the Reddit API
python tests/test_reddit_connection.py

# Test email delivery
python tests/test_email_connection.py

# Run the full system test
python tests/test_full_system.py
```

### Database

The project uses a PostgreSQL database (Schema V2) for storage:

- **subreddits** — Manages subreddit metadata and the daily trending-post cache (`daily_hot_post_ids`)
- **reddit_posts** — Stores post content and GPT summaries (including `score`, `fetch_date`, and `gpt_summary`)
- **newsletter_logs** — Stores global newsletter delivery logs
- Optional: **users** and **user_newsletter_logs** — Store users and personalized delivery logs (for future expansion)

The database connection is configured through the `DATABASE_URL` environment variable. The required tables are initialized automatically when the system starts (see [docs/database_schema_v2.md](docs/database_schema_v2.md)).

### Contributing

Issues and pull requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## 📄 License

This project is open source under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PRAW](https://github.com/praw-dev/praw) - Reddit API client
- [OpenAI](https://openai.com/) - GPT API service
