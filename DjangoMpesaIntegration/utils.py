import logging
import math
import time
import base64
import requests
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

    def __init__(self):
        now = datetime.now()
        self.shortcode = settings.SHORT_CODE
        self.consumer_key = settings.CONSUMER_KEY
        self.consumer_secret = settings.CONSUMER_SECRET
        self.access_token_url = settings.ACCESS_TOKEN_URL

        self.password = self.generate_password()
        self.callback_url = self.CALLBACK_URL
        self.checkout_url = settings.CHECKOUT_URL

        try:
            self.access_token = self.getAccessToken()
            if self.access_token is None:
                raise Exception('Request for access token failed!')
        except Exception as e:
            logging.error('Error {}'.format(e))
        else:
            self.access_token_expiration = time.time() + 3400

    
    def getAccessToken(self):
        try:
            res = requests.get(
                self.access_token_url,
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret)
            )
        except Exception as err:
            logging.error('Error {}'.format(err))
            raise err
        else:
            token = res.json()['access_token']
            self.headers = {'Authorization': f'Bearer {token}'}
            return token
        