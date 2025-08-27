# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-27

### Added
- Initial release of Reddit Newsletter Bot
- Reddit API integration using PRAW library
- Automated newsletter generation from hot Reddit posts
- Email sending functionality with HTML templates
- SQLite database for tracking sent posts and statistics
- Scheduled sending with configurable time
- Configuration management with environment variables
- Comprehensive test suite
- Management tools for testing and administration
- Support for multiple subreddits
- NSFW content filtering
- Duplicate post prevention
- Email template customization
- Logging system with file and console output
- Statistics tracking and reporting

### Features
- **Reddit Integration**: Fetch hot posts from configurable subreddits
- **Email Newsletter**: Send formatted HTML newsletters via SMTP
- **Database Management**: SQLite database for post tracking and statistics
- **Scheduling**: Daily automated sending at configurable times
- **Configuration**: Environment-based configuration with validation
- **Testing**: Comprehensive test suite and management tools
- **Logging**: Detailed logging with configurable levels
- **Templates**: Customizable HTML and text email templates

### Tools
- `tools/manage.py` - Main management script
- `tools/preview_server.py` - Email template preview server
- `tools/oauth_helper.py` - Reddit OAuth setup assistant
- `tests/run_tests.py` - Test runner
- Individual test modules for each component

### Configuration
- Reddit API credentials
- SMTP email server settings
- Target subreddits and post limits
- Email recipients
- Schedule timing
- Content filtering options
