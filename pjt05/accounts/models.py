from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nickname = models.CharField(max_length=50)
    interest_stocks = models.CharField(max_length=200, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    
    # 신규 설문조사 필드
    investment_experience = models.CharField(max_length=20, blank=True, null=True)
    risk_tolerance = models.CharField(max_length=20, blank=True, null=True)
    investment_goal = models.CharField(max_length=20, blank=True, null=True)
