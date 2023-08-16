import logging
import uuid
from model_utils.models import TimeStampedModel
from django.db import models
from simple_history.models import HistoricalRecords
# from completion.models import BlockCompletion

logger = logging.getLogger(__name__)


class EducontStatisticsItem(models.Model):
    '''
    "statisticType": "ENTER_TO_STUDY_SUBJECT",
    "externalId": "rus_1_11",
    "status": "true",
    "createdAt": "2022-01-25T08:08:55.125Z",
    "profileId": "9d0b9750-5ad9-4311-a0bc-06ab85eddc04"
    '''

    TYPES = (('s', 'ENTER_TO_STUDY_SUBJECT'), ('e', 'ENTER_TO_EDUCATION_PLATFORM'))
    statisticType = models.CharField("statisticType", max_length=2, choices=TYPES)
    externalId = models.CharField("externalId", max_length=255, default="")
    status = models.BooleanField("Status", blank=True, null=True)
    profileId = models.UUIDField("id профиля пользователя в системе Educont")
    createdAt = models.DateTimeField(auto_now_add=True)

    transaction = models.ForeignKey("Transaction", blank=True, null=True, on_delete=models.PROTECT)


class TransactionStatus(models.TextChoices):
    __empty__ = 'CREATED'  # Данные отправлены, получен ид транзакции, статус не запрашивался
    IN_WAITING = 'IN_WAITING', 'IN_WAITING'  # статистика находится в очереди на обработку, требуется отправить запрос на получение статуса обработки позднее
    IN_PROCESSING = 'IN_PROCESSING', 'IN_PROCESSING'  # статистика получена из очереди, находится в процессе обработки, требуется отправить запрос на получение статуса обработки позднее;
    COMPLETED = 'COMPLETED', 'COMPLETED'  # статистика успешно загружена
    WITH_ERRORS = 'WITH_ERRORS', 'WITH_ERRORS'  # статистика успешно загружена, но есть ошибочные записи, которые были отклонены, необходимо их проверить вручную и если требуется, то перезагрузить
    FAILED = 'FAILED', 'FAILED'  # статистика отклонена по технической причине, необходимо перезагрузить


class Transaction(TimeStampedModel):
    id = models.CharField(max_length=36, default=uuid.uuid4, unique=True, primary_key=True)
    status = models.CharField(max_length=16, blank=True, choices=TransactionStatus.choices)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.id} - {TransactionStatus(self.status).label}'

class TransactionErrorMessage(models.Model):
    message = models.TextField()
    transaction = models.ForeignKey(Transaction, related_name='error_messages', on_delete=models.CASCADE)
    fixed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.transaction} - {self.message} - {self.fixed}'

    # TODO: add post_save to Transaction. Check status != WITH_ERRORS and fix related error messages
