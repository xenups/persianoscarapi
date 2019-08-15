from django.db import models


class Payment(models.Model):
    """
    This model use for registeration payments.
    """

    full_name = models.CharField(
        verbose_name="نام و نام خانوادگی", max_length=255, blank=True, null=True
    )
    amount = models.BigIntegerField(
        verbose_name="مبلغ"
    )
    mobile = models.CharField(
        verbose_name="شماره موبایل", max_length=11, blank=True, null=True
    )
    token = models.CharField(max_length=20,verbose_name="token",blank=False,null=False)
    description = models.CharField(
        verbose_name="توضیحات", max_length=255, blank=True, null=True
    )
    transid = models.IntegerField(
        verbose_name="شماره فاکتور"
    )
    factor_number = models.IntegerField(
        verbose_name="شماره فاکتور"
    )
    status = models.BooleanField(
        verbose_name="وضعیت", default=False
    )
    card_number = models.CharField(
        verbose_name="شماره کارت", max_length=18, blank=True, null=True
    )
    trace_number = models.CharField(
        verbose_name="شماره پیگیری", max_length=255, blank=True, null=True
    )
    message = models.TextField(
        verbose_name="پیام", blank=True, null=True
    )
    insert_date_time = models.DateTimeField(
        auto_now_add=True, verbose_name="زمان ایجاد"
    )
    payment_date_time = models.DateTimeField(
        auto_now=True, verbose_name="زمان پرداخت"
    )

    def __str__(self):
        return "TransID: {}, Amount: {}".format(self.transid, self.amount)

    def get_status(self):
        if self.status == 1:
            status = "پرداخت شده"
        else:
            status = "پرداخت نشده"
        return status
    get_status.short_description = 'وضعیت'

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت ها"
        ordering = ["-payment_date_time"]
