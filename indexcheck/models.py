from django.db import models
from django.utils import timezone
from django_mysql.models import ListCharField

class Indexcheck(models.Model):
    theme_name = models.CharField('テーマ名', max_length=255)
    code = ListCharField(
        models.CharField('コード', max_length=255,), max_length=(1 * 15))
    created_at = models.DateTimeField('作成日', default=timezone.now)
    #comment = models.TextField('コメント', blank=True)

    def __str__(self):
        return self.theme_name
