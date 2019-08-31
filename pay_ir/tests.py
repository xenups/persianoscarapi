from django.test import TestCase, Client
from django.urls import reverse
from pay_ir.models import Payment


class MainTests(TestCase):

    c = Client()

    def setUp(self):
        Payment.objects.create(full_name="John Hana",
                               amount="16700", transid=1)
        Payment.objects.create(full_name="John Whick",
                               amount="22000000", transid=2, status=1)

    def test_get_data(self):
        hana = Payment.objects.get(transid=1)
        whick = Payment.objects.get(transid=2)
        self.assertEqual(hana.full_name, "John Hana")
        self.assertEqual(whick.amount, 22000000)
        self.assertEqual(hana.__str__(), "TransID: 1, Amount: 16700")

    def test_get_status_func(self):
        hana = Payment.objects.get(transid=1)
        whick = Payment.objects.get(transid=2)
        self.assertEqual(hana.status, False)
        self.assertNotEqual(whick.status, False)
        self.assertEqual(hana.get_status(), "پرداخت نشده")
        self.assertEqual(whick.get_status(), "پرداخت شده")

    def test_index_page(self):
        response = self.c.get(reverse('index'))
        self.assertTemplateUsed(response=response, template_name='payir_index.html')

    def test_payment_request_bad_method(self):
        response = self.c.get(reverse('req_page'))
        self.assertEqual(response.status_code, 405)

    def test_payment_request_seccess(self):
        response = self.c.post(path=reverse('req_page'), data={
            "fullname": "Rasooll",
            "amount": "22000",
            "mobile": "09123456789",
            "description": "for test"
        })
        self.assertEqual(response.status_code, 302)

    def test_payment_request_fail(self):
        response = self.c.post(path=reverse('req_page'))
        self.assertEqual(response.status_code, 400)

    def test_payment_verify_bad_method(self):
        response = self.c.get(reverse('verify'))
        self.assertEqual(response.status_code, 405)

    def test_payment_verify_fail(self):
        response = self.c.post(reverse('verify'), data={
            "status": 0
        })
        self.assertTemplateUsed(response=response, template_name='payir_fail.html')

    def test_payment_verify_middle(self):
        response = self.c.post(reverse('verify'), data={
            "status": 1,
            "transId": "",
            "message": "OK",
            "cardNumber": "9634*****6578",
            "traceNumber": "876858"
        })
        self.assertTemplateUsed(response=response, template_name='payir_fail.html')
