from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager as AuthUserManager 
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from importlib import import_module


SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


class UserManager(AuthUserManager):
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('sex', 'm')
        return super().create_superuser(username, email, password, **extra_fields)

class User(AbstractUser):
    sex = models.CharField(
            max_length=1,
            choices=(
                ('f', 'female'),
                ('m', 'male'),
            ),
            verbose_name='성별')

    objects = UserManager()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    website_url = models.URLField(blank=True)


def on_post_save_for_user(sender, **kwargs):
    if kwargs['created']:
        # 가입시기
        user = kwargs['instance']

        # 환영 이메일 보내기
        send_mail(
            '환영합니다.',
            'Here is the message.',
            'wlckd90@gmail.com',
            [user.email],
            fail_silently=False,
        )

# User 회원 가입 시 Profile 생성하기
# post_save.connect 첫번쨰 인자는 실행 함수고 두번째 인자는 특정 모델 생성 후 실행하겠다는 뜻
post_save.connect(on_post_save_for_user, sender=settings.AUTH_USER_MODEL)


class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    session_key = models.CharField(max_length=40, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


def kicked_my_other_sessions(sender, request, user, **kwargs):
    for user_session in UserSession.objects.filter(user=user):
        session_key = user_session.session_key
        session = SessionStore(session_key)
        # session.delete()
        session['kicked'] = True
        session.save()
        user_session.delete()

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    UserSession.objects.create(user=user, session_key=session_key)

"""
    s = SessionStore()
    s.create()
    # session_key = request.session.session_key
    session_key = s.session_key
    UserSession.objects.create(user=user, session_key=session_key)
    session.save()
    """

user_logged_in.connect(kicked_my_other_sessions, dispatch_uid='user_logged_in')
