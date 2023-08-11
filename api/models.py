from django.db import models
from api.enums import WalletStatusEnum
from api.library import generate_key
from api.enums import GenerateKeyTypeEnum


class Customers(models.Model):
    id = models.AutoField(primary_key=True)
    customer_xid = models.CharField(max_length=50, blank=False, unique=True)


class Authentications(models.Model):
    id = models.AutoField(primary_key=True)
    customer_xid = models.CharField(max_length=50, null=False, blank=False)
    token = models.CharField(
        max_length=50, blank=False, unique=True)


class Wallets(models.Model):
    id = models.CharField(max_length=50, primary_key=True, unique=True)
    owned_by = models.CharField(
        max_length=50, null=False, blank=False, unique=True)
    status = models.CharField(
        max_length=20, choices=WalletStatusEnum.choices(), blank=True, null=True)
    enabled_at = models.DateTimeField(blank=True, null=True)
    balance = models.IntegerField(default=0)


class Withdrawals(models.Model):
    id = models.CharField(max_length=50, primary_key=True, unique=True)
    withdrawn_by = models.CharField(max_length=50, null=False, blank=False)
    status = models.CharField(
        max_length=20, choices=WalletStatusEnum.choices(), blank=True, null=True)
    withdrawn_at = models.DateTimeField(blank=True, null=True)
    amount = models.IntegerField(default=0)
    reference_id = models.CharField(max_length=50)


class Deposits(models.Model):
    id = models.CharField(max_length=50, primary_key=True, unique=True)
    deposit_by = models.CharField(max_length=50, null=False, blank=False)
    status = models.CharField(
        max_length=20, choices=WalletStatusEnum.choices(), blank=True, null=True)
    deposit_at = models.DateTimeField(blank=True, null=True)
    amount = models.IntegerField(default=0, null=False, blank=False)
    reference_id = models.CharField(max_length=50, null=False, blank=False)
