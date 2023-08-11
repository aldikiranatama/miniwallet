from functools import wraps
from api.models import Authentications
from rest_framework import status
from rest_framework.response import Response


def authentication_token(function):
    @wraps(function)
    def wrapper_func(self, request, *args, **kwargs):

        try:
            authorization = request.META.get('HTTP_AUTHORIZATION', b'')
            token = authorization.split(" ")[1]
            auth_data = Authentications.objects.get(token=token)
        except:
            return Response({"status": "unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        request.session['customer_xid'] = auth_data.customer_xid

        return function(self, request, *args, **kwargs)

    return wrapper_func
