from rest_framework import serializers
from api.models import Customers, Authentications, Wallets, Withdrawals, Deposits
from api.enums import WalletStatusEnum, TransactionStatusEnum, ApiMethodEnum, GenerateKeyTypeEnum
from datetime import datetime
from api.library import generate_key


class CustomerSerializer(serializers.ModelSerializer):
    customer_xid = serializers.CharField(
        max_length=50, required=True)

    class Meta:
        model = Customers
        fields = ('__all__')

    def validate(self, validate_data):
        data = dict(validate_data)

        customer_xid = data.get("customer_xid")
        customer = None
        try:
            customer = Customers.objects.get(customer_xid=customer_xid)
        except:
            pass

        if customer:
            raise serializers.ValidationError(
                {"error": "customer_xid already exist"})

        return data

    def create(self, validated_data):

        customer_xid = validated_data.get("customer_xid")

        Customers.objects.create(**validated_data)

        # create authentication
        data_auth = validated_data
        data_auth['token'] = generate_key(
            GenerateKeyTypeEnum.TOKEN.name, customer_xid)
        result_auth = Authentications.objects.create(**validated_data)
        result_auth = {"token": result_auth.token}

        # create wallet
        data = dict()
        data["owned_by"] = customer_xid
        data["id"] = generate_key(GenerateKeyTypeEnum.ID.name, customer_xid)
        result_wallet = Wallets.objects.create(**data)

        return result_auth


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallets
        fields = ('__all__')

    def validate(self, validated_data):
        data = dict(validated_data)
        method = self.context.get("method")
        is_disable = self.context.get('is_disable')
        owned_by = self.context.get('owned_by')

        try:
            wallet = Wallets.objects.get(owned_by=owned_by)
        except:
            raise serializers.ValidationError({"wallet": "not found"})

        if method == ApiMethodEnum.POST.name:
            if wallet.status == WalletStatusEnum.ENABLED.name:
                raise serializers.ValidationError(
                    {"wallet": "already enabled"})

        if method == ApiMethodEnum.PATCH.name:
            if wallet.status == WalletStatusEnum.DISABLED.name:
                raise serializers.ValidationError(
                    {"error": "already disabled"})

            if not is_disable:
                raise serializers.ValidationError(
                    {"error": "is_disable true required"})

        return data

    def create(self, validated_data):
        return Wallets.objects.create(**validated_data)


class WithdrawalSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(required=True)
    reference_id = serializers.CharField(required=True, max_length=50)

    class Meta:
        model = Withdrawals
        fields = ('__all__')

    def to_internal_value(self, data):
        data = dict(data)
        withdrawn_by = self.context.get("withdrawn_by")
        reference_id = data.get('reference_id')[0]
        join_id = withdrawn_by + reference_id

        data['id'] = generate_key(
            GenerateKeyTypeEnum.ID.name, join_id)
        data['withdrawn_by'] = withdrawn_by
        data['amount'] = data.get('amount')[0]
        data['reference_id'] = reference_id

        return data

    def validate(self, validated_data):
        data = dict(validated_data)

        cust_withdrawn = None
        try:
            cust_withdrawn = Withdrawals.objects.get(
                withdrawn_by=data.get('withdrawn_by'), reference_id=data.get('reference_id'))
        except:
            pass

        if cust_withdrawn:
            raise serializers.ValidationError(
                {"error": "reference_id already exist"}
            )

        try:
            cust_wallet = Wallets.objects.get(
                owned_by=data['withdrawn_by'])
        except:
            raise serializers.ValidationError(
                {"error": "wallet not found"}
            )

        wallet_status = cust_wallet.status
        wallet_balance = cust_wallet.balance

        if wallet_status == None:
            raise serializers.ValidationError(
                {"error": "wallet not found"}
            )

        if wallet_status == WalletStatusEnum.DISABLED.name:
            raise serializers.ValidationError(
                {"error": "wallet disabled"}
            )

        if wallet_balance < int(data.get('amount')[0]):
            raise serializers.ValidationError(
                {"error": "not enough balance"}
            )

        return data

    def create(self, data):
        # create deposit
        data['withdrawn_at'] = datetime.utcnow()
        data['status'] = TransactionStatusEnum.SUCCESS.name
        withdrawn = Withdrawals.objects.create(**data)

        # adjust wallet balance
        withdrawn_by = data.get('withdrawn_by')
        wallet = Wallets.objects.get(owned_by=withdrawn_by)
        new_balance = int(wallet.balance) - int(withdrawn.amount)
        wallet.balance = new_balance
        wallet.save()

        return withdrawn


class DepositSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(required=True)
    deposit_by = serializers.CharField(required=True)
    reference_id = serializers.CharField(max_length=50, required=True)

    class Meta:
        model = Deposits
        fields = ('__all__')

    def to_internal_value(self, data):
        data = dict(data)
        deposit_by = self.context.get("deposit_by")
        reference_id = data.get('reference_id')[0]
        join_id = deposit_by + reference_id

        data['id'] = generate_key(
            GenerateKeyTypeEnum.ID.name, join_id)
        data['deposit_by'] = deposit_by
        data['deposit_at'] = datetime.utcnow()
        data['status'] = TransactionStatusEnum.SUCCESS.name
        data['amount'] = data.get('amount')[0]
        data['reference_id'] = reference_id

        return data

    def validate(self, data):

        cust_deposit = None
        try:
            cust_deposit = Deposits.objects.get(
                deposit_by=data.get('deposit_by'), reference_id=data.get('reference_id'))
        except:
            pass

        if cust_deposit:
            raise serializers.ValidationError(
                {"error": "reference_id already exist"}
            )

        try:
            cust_wallet = Wallets.objects.get(
                owned_by=data.get('deposit_by'))
        except:
            raise serializers.ValidationError({"error": "wallet not found"})

        wallet_status = cust_wallet.status

        if wallet_status == None:
            raise serializers.ValidationError(
                {"error": "wallet not found"}
            )

        if wallet_status == WalletStatusEnum.DISABLED.name:
            raise serializers.ValidationError(
                {"error": "wallet disabled"}
            )

        return data

    def create(self, data):

        # create deposit
        data['deposit_at'] = datetime.utcnow()
        data['status'] = TransactionStatusEnum.SUCCESS.name
        deposit = Deposits.objects.create(**data)

        # adjust wallet balance
        deposit_by = data.get('deposit_by')
        wallet = Wallets.objects.get(owned_by=deposit_by)
        new_balance = int(deposit.amount) + int(wallet.balance)
        wallet.balance = new_balance
        wallet.save()

        return deposit
