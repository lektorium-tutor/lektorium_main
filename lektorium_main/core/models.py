import logging
import uuid

from django.db import models
from model_utils.models import TimeStampedModel

logger = logging.getLogger(__name__)


class BaseModel(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
