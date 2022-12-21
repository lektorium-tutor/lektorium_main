from openedx.core.djangoapps.user_authn.exceptions import AuthFailedError
from social_core.exceptions import AuthAlreadyAssociated
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core import exceptions as social_exceptions     
from django.http import HttpResponse
from common.djangoapps.edxmako.shortcuts import render_to_response
from django.shortcuts import redirect
from django.contrib import messages

class EducontAuthAlreadyAssociatedMiddleware(SocialAuthExceptionMiddleware):
    """Redirect users to desired-url when AuthAlreadyAssociated exception occurs."""
    def process_exception(self, request, exception):
        if hasattr(social_exceptions, exception.__class__.__name__):
            # Here you can handle the exception as you wish
            messages.error(request, "Govno" )
            return redirect('dashboard')
        else:
            return super(EducontAuthAlreadyAssociatedMiddleware, self).process_exception(request, exception)