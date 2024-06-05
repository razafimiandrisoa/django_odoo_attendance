import os
import pytz
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def check_connexion():
    "Method to check connection internet and host"
    try:
        requests.head(os.getenv('ODOO_URL'), timeout=5)
        return True
    except:
        return False


def format_time_render(utc_time_str):
    """Method for format datetime for render"""
    utc_time = datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S')

    antananarivo_tz = pytz.timezone('Indian/Antananarivo')
    utc_time = pytz.utc.localize(utc_time)
    antananarivo_time = utc_time.astimezone(antananarivo_tz)

    return antananarivo_time.strftime('%d-%m-%Y %H:%M:%S')