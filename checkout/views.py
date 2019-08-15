import os

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, request
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from guardian.shortcuts import assign_perm
from oscar.apps.checkout.views import PaymentDetailsView as BasePaymentDetailsView, \
    ThankYouView as ThankYouViewBasement, OrderPlacementMixin, Basket
from oscar.apps.payment.admin import SourceType
from oscar.apps.payment.models import Source
from paymentexpress.gateway import PURCHASE
from urllib3 import get_host

import digital
from checkout.tasks import download_process
from digital import views
from oscar.apps.payment.exceptions import *
import requests
import datetime
from oscar.apps.payment.forms import BankcardForm

# Create your views here.
from digital.models import Abstractdigital
from shopify2 import settings

from pay_ir.models import Payment
import json
import requests


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


class globals():
    dl_link = ""


class PaymentDetailsView(BasePaymentDetailsView):
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
            globals.dl_link = address
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
        ctx['download_link'] = globals.dl_link
        key = 'order_{}_thankyou_viewed'.format(ctx['order'].pk)
        if not self.request.session.get(key, False):
            self.request.session[key] = True
            ctx['send_analytics_event'] = True
        else:
            ctx['send_analytics_event'] = False

        return ctx
