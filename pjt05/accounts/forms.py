from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    INTEREST_CHOICES = [
        ('KOSPI 주식', 'KOSPI 주식'),
        ('KOSDAQ 주식', 'KOSDAQ 주식'),
        ('금', '금'),
        ('미국 주식', '미국 주식 (S&P 500)'),
        ('국채', '국채'),
        ('비트코인', '비트코인'),
    ]
    interest_stocks = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='관심 종목'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('nickname', 'profile_image',)

    def save(self, commit=True):
        user = super().save(commit=False)
        interest_list = self.cleaned_data.get('interest_stocks', [])
        user.interest_stocks = ",".join(interest_list)
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('nickname', 'profile_image', 'interest_stocks')
