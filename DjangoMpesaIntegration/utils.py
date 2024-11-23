import logging
import math
import time
import base64
from datetime import datetime
from requests.auth import HTTPBasicAuth
from rest_framework.response import Response
from phonenumber_field.phonenumber import PhoneNumber

from django.conf import settings
from .models import Transaction
from .serializer import TransactionSerializer

logging = logging.getLogger("default")


class MpesaGateWay:
    shortcode = None
    consumer_key = None
    consumer_secret = None
    access_token_url = None
    access_token = None
    access_token_expiration = None
    checkout_url = None
    timestamp = None

    