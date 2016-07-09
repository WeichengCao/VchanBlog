# -*- coding: utf-8 -*-

from defines import *
from flask_login import login_user, logout_user, login_required, current_user
from flask_principal import identity_changed, AnonymousIdentity, Identity
from flask import render_template, redirect, request, flash, url_for, current_app, session
from flask.views import MethodView
from permissions import admin_permission, su_permission

import forms
import models
import datetime

def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.CUser.objects.get(username=form.username.data)
        except models.CUser.DoesNotExist:
            user = None

        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            user.last_login = datetime.datetime.now
            user.save()
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.username))
            return redirect(request.args.get("next") or url_for("blog_admin.index"))

        flash("Invalid username or password", "danger")

    return render_template("accounts/login.html", form=form)

@login_required
def logout():
    logout_user()

    for key in ("identity.name", "identity.auth_type"):
        session.pop(key, None)

    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    flash("You have been logged out", "success")
    return redirect(url_for("accounts.login"))

def register(create_su=False):
    if not VchanBlogSettings["allow_registration"]:
        msg = "Register is forbidden, please contact administrator"
        return msg
    if create_su and not VchanBlogSettings["allow_su_creation"]:
        msg = "Register superuser is forbidden, please contact administrator"
        return msg

    form = forms.RegistrationForm()
    if form.validate_on_submit():
        user = models.CUser()
        user.username = form.username.data
        user.password = form.password.data
        user.email = form.email.data

        user.display_name = user.username

        if create_su and VchanBlogSettings["allow_su_creation"]:
            user.is_superuser = True

        user.save()

        return redirect(url_for("main.index"))

    return render_template("accounts/registration.html", form=form)

@login_required
def add_user():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        user = models.CUser()
        user.username = form.username.data
        user.password = form.password.data
        user.email = form.email.data
        user.display_name = user.username
        user.save()
        return redirect(url_for("accounts.users"))
    return render_template("accounts/registration.html")

def get_current_user():
    user = models.CUser.objects.get(username=current_user.username)
    return user


class Profile(MethodView):
    decorators = [login_required]
    template_name = "accounts/settings.html"

    def get(self, form=None):
        if not form:
            user = current_user
            user.weibo = user.social_networks["weibo"].get("url")
            user.weixin = user.social_networks["weixin"].get("url")
            user.twitter = user.social_networks["twitter"].get("url")
            user.github = user.social_networks["github"].get("url")
            user.facebook = user.social_networks["facebook"].get("url")
            user.linkedin = user.social_networks["linkedin"].get("url")
            form = forms.ProfileForm(obj=user)
        data = {"form":form}
        return render_template(self.template_name, **data)

    def post(self):
        form = forms.ProfileForm(obj=request.form)
        if form.validata():
            user = current_user
            if user.email != form.email.data:
                user.email = form.email.data
                user.is_email_comfirmed = False

            user.display_name = form.display_name.data
            user.biography = form.biography.data
            user.homepage_url = form.homepage_url.data
            user.social_networks["weibo"]["url"] = form.weibo.data or None
            user.social_networks["weixin"]["url"] = form.weixin.data or None
            user.social_networks["twitter"]["url"] = form.twitter.data or None
            user.social_networks["github"]["url"] = form.github.data or None
            user.social_networks["facebook"]["url"] = form.facebook.data or None
            user.social_networks["linkedin"]["url"] = form.linkedin.data or None
            user.save()

            msg = "Succeed to update user profile"
            flash(msg, "success")

            return redirect(url_for("blog_admin.index"))

        return self.get(form)


class SuUsers(MethodView):
    decorators = [login_required, su_permission.require(401)]
    template_name = "accounts/su_users.html"
    def get(self):
        users = models.CUser.objects.all()
        return render_template(self.template_name, users=users)

class SuUser(MethodView):
    decorators = [login_required, admin_permission.require(401)]
    template_name = "accounts/user.html"

    def get_context(self, username, form=None):
        if not form:
            user = models.CUser.objects.get_or_404(username=username)
            user.weibo = user.social_networks['weibo'].get("url")
            user.weixin = user.social_networks['weixin'].get("url")
            user.twitter = user.social_networks['twitter'].get('url')
            user.github = user.social_networks['github'].get('url')
            user.facebook = user.social_networks['facebook'].get('url')
            user.linkedin = user.social_networks['linkedin'].get('url')
            form = forms.SuUserForm(obj=user)
        data={'form': form}
        return data

    def get(self, username, form=None):
        data = self.get_context(username, form)
        return render_template(self.template_name, **data)

    def post(self, username):
        form = forms.SuUserForm(obj=request.form)
        if form.validate():
            user = models.CUser.objects.get_or_404(user=username)
            user.email = form.email.data
            user.is_email_comfirmed = form.is_email_comfirmed.data

            user.display_name = form.display_name.data
            user.biography = form.biography.data
            user.homepage_url = form.homepage_url.data or None
            user.social_networks['weibo']['url'] = form.weibo.data or None
            user.social_networks['weixin']['url'] = form.weixin.data or None
            user.social_networks['twitter']['url'] = form.twitter.data or None
            user.social_networks['github']['url'] = form.github.data or None
            user.social_networks['facebook']['url'] = form.facebook.data or None
            user.social_networks['linkedin']['url'] = form.linkedin.data or None
            user.save()

            flash("Succeed to update user profile", 'success')
            return redirect(url_for('accounts.su_edit_user', username=user.username))

        return self.get(form)


class Users(MethodView):
    decorators = [login_required, admin_permission.require(401)]
    template_name = "accounts/users.html"
    def get(self):
        users = models.CUser.objects.all()
        return render_template(self.template_name, users=users)


class User(MethodView):
    decorators = [login_required, admin_permission.require(401)]
    template_name = "accounts/user.html"

    def get_context(self, username, form=None):
        if not form:
            user = models.CUser.objects.get_or_404(username=username)
            form = forms.UserForm(obj=user)
        data = {"form": form}
        return data

    def get(self, username, form=None):
        data = self.get_context(username, form)
        return render_template(self.template_name, **data)

    def post(self, username):
        form = forms.UserForm(obj=request.form)
        if form.validate():
            user = models.CUser.objects.get_or_404(username=username)
            if user.email != form.email.data:
                user.is_email_confirmed = False
            user.email = form.email.data
            user.role = form.role.data
            user.save()
            flash("Succeed to update user details", "success")
            return redirect(url_for("accounts.edit_user", username=username))
        return self.get(username, form)

    def delete(self, username):
        user = models.CUser.objects.get_or_404(username=username)
        user.delete()
        if request.args.get("ajax"):
            return "success"
        flash("Succeed to delete user", "success")
        return redirect(url_for("accounts.users"))

class Password(MethodView):
    decorators = [login_required]
    template_name = "accounts/password.html"

    def get(self, form=None):
        if not form:
            form = forms.PasswordForm()
        data = {"form": form}
        return render_template(self.template_name, **data)