# Changelog

All notable changes to the Reddit Newsletter Bot project will be documented in this file.

## [2.0.0] - 2024-12-19

### 🎉 Major Features Added

- **OpenAI GPT Integration**: Automatic content summarization and editor message generation
- **Enhanced Database**: Post history tracking with GPT summaries and newsletter logs
- **CLI Management Tools**: Comprehensive `tools.py` with testing and management commands
- **Enhanced Main Program**: `enhanced_main.py` with single-run and scheduler modes

### ✨ Improvements

- **Performance Optimization**: Reduced GPT token usage for cost efficiency
- **Better Error Handling**: Improved resilience for network timeouts and API failures
- **Code Cleanup**: Removed redundant comments and improved code structure
- **Documentation**: Complete README overhaul with badges and usage examples

### 🔧 Technical Updates

- Updated email templates with GPT content integration
- Database schema auto-upgrade system
- Better configuration management with .env.example template
- Enhanced logging and error reporting

### 🐛 Bug Fixes

- Fixed placeholder text in newsletter signatures
- Resolved GPT content formatting issues (Markdown symbol removal)
- Improved SMTP connection stability

## [1.0.0] - 2024-12-18

### 🎉 Initial Release

- Reddit API integration using PRAW library
- Automated newsletter generation from hot Reddit posts
- Email sending functionality with HTML templates
- SQLite database for tracking sent posts and statistics
- Scheduled sending with configurable time
- Configuration management with environment variables
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
