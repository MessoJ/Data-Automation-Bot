# Data Automation Bot

A Python-based bot that automates data preprocessing and reporting, integrating with APIs and SQL databases. This solution reduces manual effort and includes a modern web dashboard for monitoring and management.

## Features

- **Automated data extraction** from multiple sources (APIs and SQL databases)
- **Data cleaning and preprocessing** pipeline with advanced algorithms
- **Customizable report generation** with multiple output formats
- **Scheduled automation workflows** with robust job management
- **Modern web dashboard** for real-time monitoring and control
- **Professional admin interface** for configuration and job management
- **Real-time metrics and visualizations** with interactive charts
- **Responsive design** that works on desktop and mobile devices

## Screenshots

![Data Automation Bot Dashboard](https://github.com/user-attachments/assets/abbd33e5-a936-401d-a837-f76ddb980daf)

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/messoj/Data-Automation-Bot.git
   cd Data-Automation-Bot
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env file with your actual credentials
   ```

## Usage

### Web Dashboard (Recommended)

Start the modern web interface for full functionality:

```bash
python run_web.py
```

Then open your browser to: http://localhost:5000

The web dashboard provides:
- **Real-time monitoring** of data processing
- **Interactive report generation** and management
- **Job scheduling and control** interface
- **System configuration** management
- **Live metrics and charts** with automatic updates

### Command Line Interface

For automated/headless operation:

```bash
python main.py
```

### Scheduling automated runs

The bot can be scheduled to run at different intervals:

```bash
python main.py --schedule daily
```

## Production Deployment

For production environments, use the included deployment script:

```bash
./deploy.sh
```

This will:
- Install all dependencies
- Set up the database
- Start the application with Gunicorn
- Configure logging and monitoring

## API Endpoints

The web application exposes REST API endpoints:

- `GET /api/status` - System status and metrics
- `GET /api/data` - Retrieve processed data
- `GET /api/reports` - List available reports
- `POST /api/reports/generate` - Generate new reports
- `GET /api/jobs` - List scheduled jobs
- `GET /api/config` - View configuration

## Development

### Running tests

```bash
pytest
```

### Adding new data sources

To add a new data source, create a new connector in the `api` or `database` directories.

### Customizing the web interface

The web frontend is built with:
- **Flask** backend with RESTful APIs
- **Modern CSS Grid/Flexbox** responsive design
- **Vanilla JavaScript** with Chart.js for visualizations
- **Professional styling** with a clean, modern aesthetic

## Configuration

### Database Support

- **PostgreSQL** for production (recommended)
- **SQLite** for development and testing (automatic fallback)

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DB_HOST=localhost
DB_PASSWORD=your_password
DB_NAME=data_automation

# API Configuration
API_KEY=your_api_key
API_BASE_URL=https://api.example.com/v1

# Scheduler
SCHEDULER_INTERVAL=3600  # seconds

# Web Application
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
```

## Architecture

- **Backend**: Python with Flask, SQLAlchemy, APScheduler
- **Frontend**: Modern HTML5/CSS3/JavaScript with responsive design
- **Database**: PostgreSQL/SQLite with automated migrations
- **Scheduling**: APScheduler with job management
- **Reporting**: Multiple formats (HTML, CSV, JSON) with visualizations

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in the `/docs` directory
- Review the API documentation at `/api/docs` when running
