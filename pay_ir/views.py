from django.shortcuts import render, redirect
from django.http import (
    HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse
)
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
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
            "mobile": request.POST.get('mobile'),
            "factorNumber": request.POST.get("factorNumber"),
            "description": request.POST.get('description'),
            "transaction": request.POST.get('transaction'),
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
                         transid=data_dict["transaction"]
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
    print(request)
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
            data_query = Payment.objects.filter(token=token).order_by('-id')[0]
            if data_query.status == 0 and data_query.amount == int(verify["amount"]):
                data_query.status = 1
                data_query.card_number = verify["cardNumber"]
                data_query.trace_number = verify["traceNumber"]
                data_query.message = message
                data_query.save()
                data = {
                    "amount": verify["amount"],
                    "factor_number": verify["factorNumber"],
                    "mobile": verify["mobile"],
                    "description" : verify["description"],
                    "card_number" : verify["cardNumber"],
                    "trace_number" : verify["traceNumber"],
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
