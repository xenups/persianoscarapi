from django.shortcuts import render, redirect
from django.http import (
    HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse,
    Http404)
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from django.views.generic import RedirectView
from oscar.apps.checkout.mixins import OrderPlacementMixin, Basket
from oscar.apps.partner.strategy import Selector
from urllib3 import get_host

from pay_ir import models
from pay_ir.models import Payment
import json
import requests


class CustomCheckoutDone(OrderPlacementMixin, RedirectView):
    """
    here we verify payment was done and place the actual order
    then redirect to thank you page
    """
    permanent = False

    def get_redirect_url(self, ):
        basket = Basket.objects.get(pk=self.checkout_session.get_submitted_basket_id())
        basket.strategy = Selector().strategy()
        order_number = self.checkout_session.get_order_number()
        shipping_address = self.get_shipping_address(basket)
        shipping_method = self.get_shipping_method(basket, shipping_address)
        shipping_charge = shipping_method.calculate(basket)
        billing_address = self.get_billing_address(shipping_address)
        order_total = self.get_order_totals(basket, shipping_charge=shipping_charge)
        order_kwargs = {}
        # make sure payment was actually paid
        data_query = \
            Payment.objects.filter(factor_number=order_number, status=1, amount=float(order_total.incl_tax)).order_by(
                '-id')[0]
        if data_query is None:
            raise Http404
        # CustomPayment.objects.get(order_number=order_number, payed_sum=str(float(order_total.incl_tax)))
        user = self.request.user
        reference = "asan pardakht"
        if not user.is_authenticated:
            order_kwargs['guest_email'] = self.checkout_session.get_guest_email()
        self.handle_order_placement(
            order_number, user, basket, shipping_address, shipping_method,
            shipping_charge, billing_address, order_total, **order_kwargs
        )
        self.add_payment_source("asan pardakht")

        self.add_payment_event('pre-auth', order_total.incl_tax, "asan pardakht")
        return '/checkout/thank-you/'


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


def verify_trans(token):
    url = "https://pay.ir/pg/verify"
    data = {
        "api": settings.PAY_IR_CONFIG.get("api_key"),
        "token": token,
    }
    headers = {"Content-Type": "application/json", }
    resp = requests.post(url, data=json.dumps(data), headers=headers)
    print(resp)
    return resp.json()


def index(request):
    """ First page of app. """
    return render(request, "payir_index.html")


def req(request):
    """ This function call pay.ir API and redirect user to payment page. """

    if request.method == "POST":
        if request.POST.get('amount') is None:
            return HttpResponseBadRequest('Amount is required.')
        url = "https://pay.ir/pg/send"
        fullname = request.POST.get('fullname')
        headers = {
            "Content-Type": "application/json",
        }
        data_dict = {
            "api": settings.PAY_IR_CONFIG.get("api_key"),
            "amount": int(request.POST.get('amount')),
            "redirect": request.scheme + "://" + request.get_host() + reverse('verify'),
            # "redirect": 'http' + "://" + "127.0.0.1/" + 'payment/verify',
            "mobile": request.POST.get('mobile'),
            "factorNumber": request.POST.get("factorNumber"),
            "description": request.POST.get('description'),

        }
        print(data_dict)

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
            print("https://pay.ir/pg/{}".format(str(token)))
            return redirect("https://pay.ir/pg/{}".format(str(token)))
        else:
            return error_code_message(response)
        return HttpResponse(content=redirect)

    else:
        return method_not_allowed()


@csrf_exempt
def verfication(request, message=None):
    if request.method == "GET":
        status_code = int(request.GET.get("status"))
        token = request.GET.get("token")
        if status_code == 1:
            message = request.GET.get("message")

        else:
            data = {"message": message}
            return render(request, "payir_fail.html", data)
        verify = verify_trans(token)
        if verify["status"] == 1:
            data_query = Payment.objects.get(token=token, factor_number=int(verify["factorNumber"]))
            if data_query.status == 0 and data_query.amount == int(verify["amount"]):
                data_query.status = 1
                data_query.card_number = verify["cardNumber"]
                data_query.trace_number = verify["transId"]
                data_query.factor_number = int(verify["factorNumber"])
                data_query.mobile = verify["mobile"]
                data_query.description = verify["description"]
                data_query.message = message
                data_query.save()
                data = {
                    "amount": verify["amount"],
                    "factor_number": verify["factorNumber"],
                    "mobile": verify["mobile"],
                    "description": verify["description"],
                    "card_number": verify["cardNumber"],
                    "trace_number": verify["transId"],
                }
                return render(request, "payir_success.html", data)
            else:
                return render(request, "payir_duplicate.html")
        else:
            data = {
                "error": verify["errorMessage"],
                "message": "در صورت کسر پول از حساب شما تا ۳۰ دقیقه آینده بازگشت داده می‌شود."
            }
            return render(request, "payir_fail.html", data)
    else:
        return method_not_allowed()
