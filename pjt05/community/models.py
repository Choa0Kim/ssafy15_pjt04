from django.db import models


class Post(models.Model):
    """금융 자산별 토론 게시글"""
    asset_id = models.CharField(max_length=50)  # JSON 자산 id와 매칭
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=150, default="익명", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
