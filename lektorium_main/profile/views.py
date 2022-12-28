import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Profile

logger = logging.getLogger(__name__)


@csrf_exempt
def sse(request, *args, **kwargs):
    if request.method == "POST":
        profile_id = request.POST["profile_id"]
        status = request.POST["status"]
        profile = Profile.objects.get(id=profile_id)

        if status == 'APPROVED':
            profile.approve()
        elif status == 'NOT_APPROVED':
            profile.disapprove()
        return HttpResponse(json.dumps({"status": "ok"}), status=200)
    elif request.method == "GET":
        return HttpResponse(json.dumps({"status": "ok"}), status=200)
    else:
        return HttpResponse('', status=405)
