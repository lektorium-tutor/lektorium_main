import logging

from .models import Profile

logger = logging.getLogger(__name__)

def sse(request, *args, **kwargs):
    if request.method=="POST":
        profile_id = request.POST["profile_id"]
        status = request.POST("status")
        profile = Profile.objects.get(id=profile_id)

        if status == 'APPROVED':
            profile.approve()
        elif status == 'NOT_APPROVED':
            profile.disapprove()
        return {"status": 200}






