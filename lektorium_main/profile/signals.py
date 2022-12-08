from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from lektorium_main.profile.models import Profile
