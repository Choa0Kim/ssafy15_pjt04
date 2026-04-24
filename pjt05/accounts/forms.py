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
    
    EXPERIENCE_CHOICES = [
        ('초보', '주린이 (투자 경험 없음~1년)'),
        ('중수', '어느 정도 해봄 (1년~3년)'),
        ('고수', '투자의 달인 (3년 이상)'),
    ]
    RISK_CHOICES = [
        ('안정추구형', '원금 보장이 가장 중요 (안정추구형)'),
        ('위험중립형', '적당한 리스크와 수익 (위험중립형)'),
        ('적극수익추구형', '손실을 감수하더라도 높은 수익 (적극추구형)'),
    ]
    GOAL_CHOICES = [
        ('단기수익', '빠른 시세 차익'),
        ('장기투자', '장기적인 우상향과 가치 성장'),
        ('배당수익', '따박따박 들어오는 배당과 이자'),
    ]

    investment_experience = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='주식 투자를 해보신 경험이 어느 정도인가요?'
    )
    risk_tolerance = forms.ChoiceField(
        choices=RISK_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='손실을 어느 정도 감수할 수 있나요?'
    )
    investment_goal = forms.ChoiceField(
        choices=GOAL_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='투자를 통해 얻고자 하는 주된 목표는 무엇인가요?'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('nickname', 'profile_image', 'investment_experience', 'risk_tolerance', 'investment_goal')

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
        fields = ('nickname', 'profile_image', 'interest_stocks', 'investment_experience', 'risk_tolerance', 'investment_goal')
