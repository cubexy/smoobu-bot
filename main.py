import os
import sys
import logging
import calendar
from logging.handlers import RotatingFileHandler
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv


def load_config():
    load_dotenv()
    try:
        return {
            "log_filepath": os.getenv("LOG_FILEPATH"),
            "target_month": os.getenv("TARGET_MONTH"),
            "target_year": os.getenv("TARGET_YEAR"),
            "content": os.getenv("CONTENT"),
            "subtype": os.getenv("TEXT_SUBTYPE", "plain"),
            "subject": os.getenv("SUBJECT"),
            "recipient": os.getenv("RECIPIENT").split(", "),
            "sender": os.getenv("SENDER"),
            "host": os.getenv("SMTP_HOST"),
            "port": int(os.getenv("SMTP_PORT", 465)),
            "user": os.getenv("SMTP_USER"),
            "passwd": os.getenv("SMTP_PASS"),
            "apartment_id": os.getenv("APARTMENT"),
            "apartment_hash": os.getenv("APARTMENT_HASH"),
        }
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)


def setup_logging(log_filepath):
    logger = logging.getLogger("ApartmentBot")
    logger.setLevel(logging.INFO)

    # clear existing handlers to prevent duplicates if recalled
    if logger.handlers:
        logger.handlers.clear()

    file_handler = RotatingFileHandler(log_filepath, maxBytes=5 * 1024 * 1024, backupCount=2)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def send_mail(config):
    logger = logging.getLogger("ApartmentBot")
    logger.info("Attempting to send notification email...")
    try:
        msg = MIMEText(config["content"], config["subtype"])
        msg['Subject'] = config["subject"]
        msg['From'] = config["sender"]
        msg['To'] = ", ".join(config["recipient"])

        conn = SMTP(config["host"], config["port"])
        conn.set_debuglevel(False)
        conn.login(config["user"], config["passwd"])
        conn.sendmail(config["sender"], config["recipient"], msg.as_string())
        conn.quit()
        logger.info(f"Email sent successfully to {config['recipient']}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


def check_for_bookability(config):
    apart_id = config["apartment_id"]
    apart_hash = config["apartment_hash"]
    target_month = config["target_month"]
    target_year = config["target_year"]

    month_name = calendar.month_name[int(target_month)]
    get_url = f"https://login.smoobu.com/en/cockpit/widget/show-calendar-iframe/{apart_id}/{apart_hash}"
    post_url = f"https://login.smoobu.com/en/cockpit/widget/single-calendar/{apart_id}"

    with requests.Session() as s:
        s.get(get_url)
        payload = {
            "month": target_month,
            "year": target_year,
            "verificationHash": apart_hash
        }
        response = s.post(post_url, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')

        month_cal = soup.select_one(f'div.calendar:has(h2:-soup-contains("{month_name}"))')

        if not month_cal:
            raise Exception(f"{month_name} calendar section not found!")

        date_cells = month_cal.select('tbody td')
        for cell in date_cells:
            if not cell.get_text(strip=True):
                continue

            classes = cell.get("class", [])

            if "normal" not in classes:
                return True

        return False


if __name__ == '__main__':
    config = load_config()
    logger = setup_logging(config["log_filepath"])

    logger.info("--- Job Started ---")
    try:
        if check_for_bookability(config):
            logger.info("Apartment found free! Triggering email.")
            send_mail(config)
        else:
            logger.info("Apartment not free. Exiting.")
    except Exception as ex:
        logger.exception(f"Critical Failure in Main Loop: {str(ex)}")
    finally:
        logger.info("--- Job Finished ---\n")