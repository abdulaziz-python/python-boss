from django.db import models
import datetime

class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} ({self.telegram_id})"

class Chat(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.telegram_id})"

class GroupAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    is_anonymous = models.BooleanField(default=False)
    anonymous_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chat')

    def __str__(self):
        if self.is_anonymous:
            return f"Anonim admin ({self.anonymous_id}) guruhda {self.chat}"
        return f"{self.user} - Admin guruhda {self.chat}"

class BannedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    banned_at = models.DateTimeField(auto_now_add=True)
    banned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bans_issued')

    def __str__(self):
        return f"{self.user} taqiqlangan guruhda {self.chat}"

class MutedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    muted_at = models.DateTimeField(auto_now_add=True)
    muted_until = models.DateTimeField()
    muted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mutes_issued')

    def __str__(self):
        return f"{self.user} ovozi o'chirilgan guruhda {self.chat} vaqtgacha {self.muted_until}"

class Rule(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class BroadcastMessage(models.Model):
    message = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    keyboard = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Xabarni tarqatish'

    def __str__(self):
        return f"Xabarni tarqatish: {self.created_at}"

