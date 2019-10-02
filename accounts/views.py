from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, reverse, resolve_url
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView, UpdateView
from django.http import Http404
from django.urls import reverse_lazy
from .forms import SignupForm, ProfileForm
from .models import Profile

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            """
            현재 유저의 프로필을 가져오고
            받은 값으로 프로필을 갱신한다.
            """
            old_profile = request.user.profile
            old_profile.bio = form.cleaned_data['bio']
            old_profile.website_url = form.cleaned_data['website_url']
            old_profile.save()
            return redirect('profile')
    elif request.method == "GET":
        form = ProfileForm(instance=request.user.profile)
        return render(request, 'accounts/profile_form.html', {
            'form': form,
        })

# class ProfileUpdateView(UpdateView, LoginRequiredMixin):
#     model = Profile
#     form_class = ProfileForm
#     success_url = reverse_lazy('profile')

#     def get_object(self):
#         return self.request.user.profile

# profile_edit = ProfileUpdateView.as_view()

# CBV
# class SignupView(CreateView):
#     model = User
#     form_class = SignupForm
#     template_name = 'accounts/signup.html'

#     def get_success_url(self):
#         next_url = self.request.GET.get('next') or 'profile'
#         return resolve_url(next_url)

#     def form_valid(self, form):
#         user = form.save()
#         auth_login(self.request, user)
#         return redirect(self.get_success_url())

# signup = SignupView.as_view()

# FBV
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            next_url = request.GET.get('next') or 'profile'
            return redirect(next_url)
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {
        'form': form,
    })


class RequestLoginViaUrlView(PasswordResetView):
    template_name = 'accounts/request_login_via_url_form.html'
    title = '이메일을 통한 로그인'
    email_template_name = 'accounts/login_via_url.html'
    success_url = settings.LOGIN_URL


def login_via_url(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        current_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        raise Http404

    if default_token_generator.check_token(current_user, token):
        auth_login(request, current_user)
        messages.info(request, '로그인이 승인되었습니다.')
        return redirect('root')
    
    messages.error(request, '로그인이 거부되었습니다.')
    return redirect('root')

class MyPasswordChangeView(PasswordChangeView):
    success_url=reverse_lazy('profile')
    template_name='accounts/password_change_form.html'
    
    def form_valid(self, form):
        messages.info(self.request, '암호 변경을 완료했습니다.')
        return super().form_valid(form)


class MyPasswordResetView(PasswordResetView):
    success_url=reverse_lazy('login')
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset.html'
    # html_email_template_name = ...

    def form_valid(self, form):
        messages.info(self.request, '암호 변경 메일을 발송했습니다.')
        return super().form_valid(form)


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    success_url=reverse_lazy('login')
    template_name = 'accounts/password_reset_confirm.html'

    def form_valid(self, form):
        messages.info(self.request, '암호 리셋을 완료했습니다.')
        return super().form_valid(form)


# 내가 만든 것
# def signup(request):
#     if request.method == "POST":
#         form = SingupForm(request.POST)
#         if form.is_valid():
#             username = request.POST.get('username')
#             email = request.POST.get('email')
#             password1 = request.POST.get('password1')
#             try:
#                 user = User(username=username, email=email)
#                 user.set_password(password1)
#                 user.save()
#             except:
#                 return render(request, 'accounts/signup.html', {
#                     'form': form,
#                 })
#             return redirect(settings.LOGIN_URL)
#     else:
#         form = SingupForm()
#     return render(request, 'accounts/signup.html', {
#         'form': form,
#     })

# UserCreationForm로 구현
# def signup(request):
#     if request.method == "POST":
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             return redirect(settings.LOGIN_URL)
#     else:
#         form = UserCreationForm()
#     return render(request, 'accounts/signup.html', {
#         'form': form,
#     })