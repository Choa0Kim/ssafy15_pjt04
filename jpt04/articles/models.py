from django.db import models

class Post(models.Model):
    asset_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(default="익명")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
