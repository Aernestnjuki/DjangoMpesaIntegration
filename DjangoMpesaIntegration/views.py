from django.shortcuts import render

import logging
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

from .serializer import MpesaCheckoutSerializer
from .utils import MpesaGateWay

gateway = MpesaGateWay()

@authentication_classes([])
@permission_classes((AllowAny,))
class MpesaCheckout(APIView):
    serializer = MpesaCheckoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            payload = {"data": serializer.validated_data, "request": request}
            res = gateway.stk_push_request(payload)
            return Response(res, status=status.HTTP_201_CREATED)
        

@authentication_classes([])
@permission_classes((AllowAny,))
class MpesaCallBack(APIView):
    def get(self, requst):
        return Response({'status': 'Ok'}, status=status.HTTP_200_OK)



    def post(self, request, *args, **kwargs):
        logging.info("{}".format("Callback from MPESA"))
        data = request.body
        return gateway.callback(json.loads(data))
    
        

