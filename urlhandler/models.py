from django.db import models
from django.contrib.auth.models import User

class shorturl(models.Model):
    original_url = models.URLField()
    short_query = models.CharField(max_length=8)
    visits = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_query
