from django.db import models

class Users(models.Model):
    userChatTelegramId = models.CharField(max_length=255, verbose_name='Id Telegram пользователя')
    phone = models.CharField(max_length=255, blank=True, verbose_name='Телефон')
    firstName = models.CharField(max_length=255, blank=True, verbose_name='Имя')
    lastName = models.CharField(max_length=255, blank=True, verbose_name='Фамилия')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TeleOrders(models.Model):
    userChatTelegramId = models.CharField(max_length=255, verbose_name='Id Telegram пользователя')
    cost = models.CharField(max_length=255, verbose_name='Цена товара')
    name = models.CharField(max_length=255, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание')
    messages = models.JSONField(verbose_name='Сообщения', blank=True)
    payStatus = models.BooleanField(verbose_name='Статус оплаты', default=True, null=True)
    doneStatus = models.BooleanField(verbose_name='Статус завершения', default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

