import os
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, request, \
    Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from oscar.apps.checkout.views import PaymentDetailsView as BasePaymentDetailsView, \
    ThankYouView as ThankYouViewBasement, OrderPlacementMixin, Basket
from django.views.generic import RedirectView
from oscar.apps.checkout.mixins import OrderPlacementMixin, Basket
from oscar.apps.partner.strategy import Selector
from oscar.apps.payment import models
from oscar.apps.payment.exceptions import *
from digital.models import Abstractdigital
from shopify2 import settings

from pay_ir.models import Payment
import json
import requests


class Globals:
    dl_link = ""


def method_not_allowed():
    """ This function only used when only POST method availabe. """

    return HttpResponseNotAllowed(
        ["POST"],
        content=json.dumps({"details": "Method not allowed"}),
        content_type="application/json"
    )


def error_code_message(response):
    return HttpResponse(content="({}): {}".format(
        response["errorCode"], response["errorMessage"]
    ))


class CustomCheckoutDone(OrderPlacementMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, ):
        try:
            basket = Basket.objects.get(pk=self.checkout_session.get_submitted_basket_id())
        except Basket.DoesNotExist:
            return reverse_lazy('checkout:preview')

        shipping_address = self.get_shipping_address(basket)
        billing_address = self.get_billing_address(shipping_address=shipping_address)
        basket.strategy = Selector().strategy()
        order_number = self.checkout_session.get_order_number()
        shipping_address = self.get_shipping_address(basket)
        shipping_method = self.get_shipping_method(basket, shipping_address)
        shipping_charge = shipping_method.calculate(basket)
        billing_address = self.get_billing_address(shipping_address)
        order_total = self.get_order_totals(basket, shipping_charge=shipping_charge)
        order_kwargs = {}

        # make sure payment was actually paid
        try:
            data_query = \
                Payment.objects.get(factor_number=order_number, status=1, amount=float(order_total.incl_tax))
        except Payment.DoesNotExist:
            # if payment was not going in correct way it will return to checkoutperview
            data_query = None
            self.restore_frozen_basket()
            return reverse_lazy('checkout:preview')
        user = self.request.user
        if not user.is_authenticated:
            order_kwargs['guest_email'] = self.checkout_session.get_guest_email()

        self.handle_order_placement(
            order_number, user, basket, shipping_address, shipping_method,
            shipping_charge, billing_address, order_total, **order_kwargs
        )
        # source_type, is_created = models.SourceType.objects.get_or_create(
        #     name='AsanPardakht')
        # source = source_type.sources.model(
        #     source_type=source_type,
        #     amount_allocated=19500,
        # )
        # self.add_payment_source(source)
        # self.add_payment_event('AsanPardakht', 19500)

        return reverse_lazy('checkout:thank-you')


class PaymentFailed(OrderPlacementMixin, RedirectView):
    def get_redirect_url(self, ):
        user = self.request.user
        if user.is_authenticated:
            self.restore_frozen_basket()
            return reverse_lazy('checkout:preview')
        raise Http404


class PaymentDetailsView(BasePaymentDetailsView):
    preview = False

    def handle_payment(self, order_number, total, **kwargs):

        print("salam khaaare jooonam")
        """ This function call pay.ir API and redirect user to payment page. """
        if total.incl_tax is None:
            return HttpResponseBadRequest('Amount is required.')
        url = "https://pay.ir/pg/send"
        fullname = "esme kharid"
        headers = {
            "Content-Type": "application/json",
        }
        data_dict = {
            "api": settings.PAY_IR_CONFIG.get("api_key"),
            "amount": int(total.incl_tax),
            # "redirect": "http" + "://" "127.0.0.1:8000" + '/payment/verify',
            "redirect": self.request.scheme + "://" + self.request.get_host() + '/payment/verify',
            "mobile": "09210419379",
            "factorNumber": order_number,
            "description": "ye kharide kheili khub",
            "transaction": order_number,
        }
        request_api = requests.post(
            url, data=json.dumps(data_dict), headers=headers
        )
        response = request_api.json()
        if response["status"] == 1:
            token = response["token"]
            db = Payment(full_name=fullname, amount=data_dict["amount"],
                         mobile=data_dict["mobile"],
                         description=data_dict["description"],
                         token=token,
                         transid=data_dict["transaction"],
                         factor_number=data_dict["factorNumber"]

                         )
            db.save()
            raise RedirectRequired("https://pay.ir/pg/{}".format(str(token)))
        else:
            return error_code_message(response)
        raise HttpResponse(content=redirect)


def handle_successful_order(self, order):
    print(self.get_message_context(order))
    queryset = Abstractdigital.objects.all()
    d = queryset.all().filter(owner=order.user)
    response = []
    for lineitem in order.lines.all():
        print(lineitem.product.video_url)
        Abstractdigital.objects.create(owner=order.user, video_url="goozbaghali.com")
        attr = lineitem.product.attr.get_all_attributes()
        # assign_perm('assign_sold', order.user, lineitem.product)
        print(order.user.has_perm('assign_sold', attr))
        print(attr)
        val = lineitem.product.attr.get_values()

        for value in val:
            dl_link = os.path.join(settings.MEDIA_ROOT, value.value.name)
            host = "http://127.0.0.1:8000/media/"
            address = host + value.value.name
            Globals.dl_link = address
            print(address)
            # these lines are just for test
            # download_process.delay(dl_link, value.value.name)
            # with open(dl_link, 'rb') as fh:
            #     response = HttpResponse(fh.read(), content_type="application/image")
            #     response['Content-Disposition'] = 'attachment; filename=' + value.value.name
            #     print(response)
            #     return response

    """
    Handle the various steps required after an order has been successfully
    placed.

    Override this view if you want to perform custom actions when an
    order is submitted.
    """
    # Send confirmation message (normally an email)
    # self.send_confirmation_message(order, self.communication_type_code)
    # print(self.get_submitted_basket())
    # Flush all session data
    self.checkout_session.flush()

    # Save order id in session so thank-you page can load it
    self.request.session['checkout_order_id'] = order.id

    response = HttpResponseRedirect(self.get_success_url())
    self.send_signal(self.request, response, order)

    return response


class ThankYouView(ThankYouViewBasement):
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        # Remember whether this view has been loaded.
        # Only send tracking information on the first load.
        ctx['somevalue'] = "دانلود ها"

        ctx['download_link'] = Globals.dl_link
        key = 'order_{}_thankyou_viewed'.format(ctx['order'].pk)
        if not self.request.session.get(key, False):
            self.request.session[key] = True
            ctx['send_analytics_event'] = True
        else:
            ctx['send_analytics_event'] = False

        return ctx
