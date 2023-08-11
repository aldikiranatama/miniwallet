import string
import random
import uuid
from api.enums import GenerateKeyTypeEnum


def generate_key(type, string_uuid=None):

    if type == GenerateKeyTypeEnum.ID.name:
        key = uuid.uuid3(uuid.NAMESPACE_X500, str(string_uuid))
    if type == GenerateKeyTypeEnum.TOKEN.name:
        key = ''.join(random.choices(
            string.ascii_lowercase + string.digits, k=40))

    return key
