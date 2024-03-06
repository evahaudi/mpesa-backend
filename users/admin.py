from django.contrib import admin

from .models import Users,PaymentTransaction


admin.site.register(PaymentTransaction)
admin.site.register(Users)
