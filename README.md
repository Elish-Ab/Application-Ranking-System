# Application Evaluation System

This system processes and ranks applications submitted via Outlook Mail using OpenAI's GPT API based on client-defined criteria. The system is modular to allow easy updates for different email providers.

## Features
- Fetch applications from Outlook using Microsoft Graph API.
- Evaluate applications based on custom criteria.
- Rank and return the top 10 applications.

## Setup and Usage

### Prerequisites
1. Python 3.8+
2. Outlook token (Microsoft Graph API).
3. OpenAI API key.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/application-evaluator.git
   cd application-evaluator
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env`:
   ```bash
   EMAIL_PROVIDER=outlook
   OUTLOOK_TOKEN=your-outlook-token
   OPENAI_API_KEY=your-openai-api-key
   ```

### Run the System
```bash
python src/main.py
```

## Extendability
- To support new email providers, create a new class in `email_provider.py` implementing the `EmailProvider` interface.
- No changes are needed in processing logic.
