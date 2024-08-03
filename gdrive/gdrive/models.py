import uuid

from django.db import models
from hashlib import sha256


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password = models.CharField(max_length=255)
    token = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        db_table = 'users'
    def __str__(self):
        return self.name

    def generate_token(self):
        data = f"{self.name}{self.id}"
        self.token = sha256(data.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.token:
            self.generate_token()
        super().save(*args, **kwargs)


class Entity(models.Model):
    folder_path = models.TextField()
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    hashpath = models.CharField(max_length=255)
    is_folder = models.BooleanField()
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE,
                                      null=True, blank=True)
    user_id = models.IntegerField(default=0)
    url = models.URLField(max_length=200)

    class Meta:
        db_table = 'entities'
    def __str__(self):
        return self.name