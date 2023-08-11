from django.contrib import admin
from .models import Customers, Authentications, Wallets, Withdrawals, Deposits

# Register your models here.
admin.site.register(Customers)
admin.site.register(Authentications)
admin.site.register(Wallets)
admin.site.register(Withdrawals)
admin.site.register(Deposits)
