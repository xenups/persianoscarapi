from django.http import HttpResponse
import json
from shopify2.celery import app
from time import sleep
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# celery
@app.task
def download_process(dl_link, name):
    print(" process called")
    # with open(dl_link, 'rb') as fh:
    #     response = HttpResponse(fh.read(), content_type="application/image")
    #     response['Content-Disposition'] = 'attachment; filename=' + name
    #     logger.info("its finished")
    # response = json.loads(response.read().decode(response.headers.get_content_charset('utf-8')))
    # return response


def girkone():
    sleep(10)
