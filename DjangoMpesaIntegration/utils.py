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


    class Decorators:
        @staticmethod
        def refresh_token(decorated):
            def wrapper(gateway, *args, **kwargs):
                if(gateway.access_token_expiration and time.time() > gateway.access_token_expiration):
                    token = gateway.getAccessToken()
                    gateway.access_token = token
                return decorated(gateway, *args, **kwargs)
            return wrapper
        
    def generate_password(self):
        """Generates mpesa api password using the provied shortcode and passkey"""

        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_str = settings.SHORT_CODE + settings.PASS_KEY + self.timestamp
        password_bytes = password_str.encode('ascii')
        return base64.b64decode(password_bytes).decode('utf-8')
    
    @Decorators.refresh_token
    def stk_push_request(self, payload):
        request = payload['request']
        data = payload['data']
        amount = data['amount']
        phone_number = data['phone_number']
        req_data = {
            'BusinessShortCode': self.shortcode,
            'Password': self.password,
            'Timestamp': self.timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': math.ceil(float(amount)),
            'PartyA': phone_number,
            'PartB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': self.callback_url,
            'AccountReference': 'Test',
            'TransactionDesc': 'Test',
        }

        res = requests.post(self.checkout_url, json=req_data, headers=self.headers, timeout=30)

        res_data = res.json()
        logging.info('Mpesa request data {}'.format(req_data))
        logging.info('Mpesa response info {}'.format(res_data))

        if res.ok:
            data['ip'] = request.META.get('REMOTE_ADDR')
            data['chockout_request-id'] = res_data['CheckoutRequstID']

            Transaction.objects.create(**data)
        return res_data
    

    