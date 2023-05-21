from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import*
from .forms import*

urlpatterns=[
    path("register", register, name="users/register"),
    path("success-account/<int:id>", success_account, name="users/success-account"),
    path("login", login_user, name="connection/login"),
    path("connexion", login_customer, name="connection/connexion"),
    path("logout", logout_user, name="logout"),
    path("users", users, name="users/users"),
    path("del-user/<int:id>", del_user, name="del_user"),
    path("detail-user/<int:id>", detail_user, name="users/detail_user"),

    path("customers", customers, name="users/customers"),
    path("details-cus/<int:id>", details_cus, name="users/details_cus"),
    path("del-customer/<int:id>", del_customer, name="del_customer"),

    path('upd-access/<int:id>', upd_access, name='users/upd_access'),
    path("profil", profile, name="users/profile"),
    path("edit-profile", edit_profile, name="users/edit_profile"),
    path("parametre", param, name="parametre"),
    path("configuration", configuration, name="users/configuration"),
    path("priority/<int:id>", priority.as_view(), name="priority"),

    path("password_change", 
         auth_views.PasswordChangeView.as_view(
            template_name="users/change-password.html", 
            success_url=reverse_lazy('password_change_done'),
            form_class=PasswordChangingForm
        ), 
        name="users/password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="users/password_change_success.html"), name="password_change_done"),

    path("reset_password", auth_views.PasswordResetView.as_view(), name="reset_password"),
    path("reset_password_sent", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset_password_complet", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("activate/<uidb64>/<token>", activate, name="activate")
]


#Mix - Dennis Ivy