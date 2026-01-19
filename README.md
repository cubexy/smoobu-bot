<h1 align="center">Smoobu Availability Monitor</h1>
<p align="center">
<img alt="Python badge" src="https://shields.io/badge/Python-3776AB?logo=Python&logoColor=FFF&style=flat-square">
</p>

A small Python script that monitors a Smoobu calendar widget for availability. If the target apartment becomes bookable for the specified month, it sends an email notification via SMTP.

## Features

-   **Calendar Scraping:** Parses the Smoobu calendar widget HTML to check for free dates.
-   **Email Alerts:** Sends an immediate notification via SMTP when availability is detected.
-   **Configurable:** Target dates, apartment credentials, and email settings are managed via `.env`.
-   **Logging:** Keeps a rotating log file of check attempts and errors.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration:**
    Copy `.env.example` to `.env` and fill in the required fields.

## Usage

### Manual Run
You can run the script manually to test the configuration:
```bash
python main.py