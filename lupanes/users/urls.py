from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

app_name = 'users'

urlpatterns = [
    path('auth/login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('auth/password_reset/',
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html',
                                              email_template_name='users/registration/password_reset_email.txt',
                                              html_email_template_name='users/registration/password_reset_email.html',
                                              subject_template_name='users/registration/password_reset_subject.txt',
                                              success_url=reverse_lazy('users:password_reset_done')),
         name='password_reset'),
    path('auth/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('auth/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                                     success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('auth/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]
