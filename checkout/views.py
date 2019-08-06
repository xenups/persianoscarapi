import os

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from guardian.shortcuts import assign_perm
from oscar.apps.checkout.views import PaymentDetailsView as BasePaymentDetailsView, ThankYouView as ThankYouViewBasement
import digital
from checkout.tasks import download_process
from digital import views

# Create your views here.
from digital.models import Abstractdigital
from shopify2 import settings


class globals():
    dl_link = ""


class PaymentDetailsView(BasePaymentDetailsView):

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
