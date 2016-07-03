# -*- coding: utf-8 -*-

from flask import Blueprint

import views

accounts = Blueprint("accounts", __name__)

accounts.add_url_rule("/login/", "login", views.login, methods=["GET", "POST"])
accounts.add_url_rule("/logout/", "logout", views.logout)
accounts.add_url_rule("/registration/", "register", views.register, methods=["GET", "POST"])
accounts.add_url_rule("/registration/su", "register_su", views.register, defaults={"create_su":True}, methods=["GET", "POST"])
accounts.add_url_rule("/add-user/", "add_user", views.add_user, methods=["GET", "POST"])
accounts.add_url_rule('/users/', view_func=views.Users.as_view('users'))
accounts.add_url_rule('/users/edit/<username>', view_func=views.User.as_view("edit_user"))
accounts.add_url_rule('/user/settings/', view_func=views.Profile.as_view('settings'))
accounts.add_url_rule('/user/password/', view_func=views.Password.as_view('password'))
accounts.add_url_rule('/su-users/', view_func=views.SuUsers.as_view('su_users'))
accounts.add_url_rule('su-users/edit/<username>', view_func=views.SuUser.as_view("su_edit_user"))