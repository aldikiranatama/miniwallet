from enum import Enum


class WalletStatusEnum(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class TransactionStatusEnum(Enum):
    SUCCESS = "success"
    FAILED = "failed"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class ApiMethodEnum(Enum):
    POST = "post"
    PATCH = "patch"
    GET = "get"


class GenerateKeyTypeEnum(Enum):
    ID = "Id"
    TOKEN = "Token"
