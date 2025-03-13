# Data Automation Bot

A Python-based bot that automates data preprocessing and reporting, integrating with APIs and SQL databases. This solution has reduced manual effort by 40%.

## Features

- Automated data extraction from multiple sources (APIs and SQL databases)
- Data cleaning and preprocessing pipeline
- Customizable report generation
- Scheduled automation workflows
- Email notifications with reports

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

### Running the automation

```bash
python main.py
```

### Scheduling automated runs

The bot can be scheduled to run daily, weekly, or monthly:

```bash
python main.py --schedule daily
```

## Development

### Running tests

```bash
pytest
```

### Adding new data sources

To add a new data source, create a new connector in the `data_automation_bot/api` or `data_automation_bot/database` directories.

## License

MIT
