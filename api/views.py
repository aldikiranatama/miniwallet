from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from api.serializers import (
    CustomerSerializer,
    WalletSerializer,
    WithdrawalSerializer,
    DepositSerializer
)
from api.enums import WalletStatusEnum, GenerateKeyTypeEnum, ApiMethodEnum
from api.models import Wallets, Deposits, Withdrawals
from api.decorators import authentication_token
from api.library import generate_key
from datetime import datetime


class CustomerView(APIView):

    def post(self, request):
        try:
            serializerCustomer = CustomerSerializer(data=request.data)
            if serializerCustomer.is_valid():
                result = serializerCustomer.save()
                return Response({"data": result, "status": "success"}, status=status.HTTP_201_CREATED)

            return Response({"data": serializerCustomer.errors, "status": "fail"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WalletView(APIView):

    @authentication_token
    def get(self, request):
        try:
            owned_by = request.session.get('customer_xid')
            message = None
            try:
                wallet = Wallets.objects.get(owned_by=owned_by)
            except:
                message = "wallet not found"

            if wallet.status == WalletStatusEnum.ENABLED.name:
                serializerWallet = WalletSerializer(wallet)
                return Response(
                    {"status": "success", "data": {"wallet": serializerWallet.data}}, status=status.HTTP_200_OK
                )

            if wallet.status == WalletStatusEnum.DISABLED.name:
                message = "wallet disabled"

            if wallet.status == None:
                message = "wallet not found"

            return Response({"status": "fail", "data": {"wallet": message}}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @authentication_token
    def post(self, request):
        try:
            owned_by = request.session.get('customer_xid')
            message = None
            try:
                wallet = Wallets.objects.get(owned_by=owned_by)
            except Exception as e:
                message = {"error": "wallet not found"}

            data = {
                "owned_by": owned_by,
                "status": WalletStatusEnum.ENABLED.name,
                "enabled_at": datetime.utcnow(),
                "method": ApiMethodEnum.POST.name
            }

            if wallet and not message:
                if wallet.status == None:
                    id = str(generate_key(
                        GenerateKeyTypeEnum.ID.name, owned_by))
                    data['id'] = id
                serializerWallet = WalletSerializer(
                    wallet, data, context=data, partial=True)
                if serializerWallet.is_valid():
                    serializerWallet.save()
                    return Response({"data": serializerWallet.data, "status": "success"}, status=status.HTTP_200_OK)

                message = serializerWallet.errors

            return Response({"data": message, "status": "fail"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @authentication_token
    def patch(self, request):
        try:
            owned_by = request.session.get('customer_xid')
            data = dict(request.data)
            message = None
            try:
                wallet = Wallets.objects.get(owned_by=owned_by)
            except:
                message = {"error": "wallet not found"}

            if wallet:
                data = {
                    "status": WalletStatusEnum.DISABLED.name,
                    "is_disable": data.get('is_disable', None),
                    "method": ApiMethodEnum.PATCH.name,
                    "owned_by": owned_by
                }

                serializerWallet = WalletSerializer(
                    wallet, data, partial=True, context=data)
                if serializerWallet.is_valid():
                    serializerWallet.save()
                    return Response({"data": serializerWallet.data, "status": "success"}, status=status.HTTP_200_OK)

                message = serializerWallet.errors

            return Response({"data": message, "status": "fail"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WithdrawalView(APIView):

    @authentication_token
    def post(self, request):
        try:
            owned_by = request.session.get('customer_xid')
            data = dict()
            data['withdrawn_by'] = owned_by

            serializerWithdraw = WithdrawalSerializer(
                data=request.data, context=data)
            if serializerWithdraw.is_valid():
                serializerWithdraw.save()
                return Response({"data": {"withdrawal": serializerWithdraw.data}, "status": "success"}, status=status.HTTP_201_CREATED)

            return Response(
                {"data": serializerWithdraw.errors, "status": "fail"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DepositView(APIView):

    @authentication_token
    def post(self, request):
        try:
            owned_by = request.session.get('customer_xid')
            data = dict()
            data['deposit_by'] = owned_by

            serializerDeposit = DepositSerializer(
                data=request.data, context=data)
            if serializerDeposit.is_valid():
                serializerDeposit.save()
                return Response(
                    {"data": {"deposit": serializerDeposit.data}, "status": "success"}, status=status.HTTP_201_CREATED
                )

            return Response(
                {"data": serializerDeposit.errors, "status": "fail"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionView(APIView):

    @authentication_token
    def get(self, request):
        try:
            customer_xid = request.session.get('customer_xid')

            try:
                deposit_trans = Deposits.objects.filter(
                    deposit_by=customer_xid
                )
                withdraw_trans = Withdrawals.objects.filter(
                    withdrawn_by=customer_xid
                )
            except:
                return Response(
                    {"status": "fail", "data": {"transactions": "Not Found"}}, status=status.HTTP_204_NO_CONTENT
                )

            serializerWithdraw = WithdrawalSerializer(
                withdraw_trans, many=True)
            serializerDeposit = DepositSerializer(deposit_trans, many=True)

            return Response(
                {
                    "status": "success",
                    "data": {
                        "deposit": serializerDeposit.data,
                        "withdrawal": serializerWithdraw.data
                    }},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
