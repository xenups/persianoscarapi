from django.contrib import admin
from pay_ir.models import Payment


class PaymentAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    list_display = ('full_name', 'transid', 'amount', 'get_status',)
    search_fields = ('transid', "trace_number", "mobile",)
    list_filter = ("status",)


admin.site.register(Payment, PaymentAdmin)
