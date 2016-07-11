# -*- coding: utf-8 -*-

from VchanBlog.defines import *
from flask import render_template, g, request, abort, url_for, flash, redirect
from flask.views import MethodView
from flask_login import login_required, current_user
from account.models import CUser
from account.permissions import writer_permission, admin_permission, editor_permission, reader_permission

import models
import forms
import datetime


def get_current_user():
    user = CUser.objects.get(username=current_user.get_id())
    return user

class AdminIndex(MethodView):
    decorators = [login_required]
    template_name = "blog_admin/index.html"

    def get(self):
        blog_meta = VchanBlogSettings["blog_meta"]
        user = get_current_user()
        return render_template(self.template_name, blog_meta=blog_meta, user=user)


class PostsList(MethodView):
    decorators = [login_required]
    template_name = "blog_admin/posts.html"

    def get(self, post_type="post"):
        posts = models.CPost.objects.filter(post_type=post_type).order_by("-update_time")

        if not g.identity.can(editor_permission):
            posts = posts.filter(author=get_current_user())

        if request.args.get("draft"):
            posts = posts.filter(is_draft=True)
        else:
            posts = posts.filter(is_draft=False)

        cur_page = request.args.get("page", 1)

        if not cur_page:
            abort(404)

        posts = posts.paginate(page=int(cur_page), per_page=10)
        return render_template(self.template_name, posts=posts, post_type=post_type)


class Post(MethodView):
    decorators = [login_required, writer_permission.require(401)]
    template_name = "blog_admin/post.html"

    def get_context(self, slug=None, form=None, post_type="post"):
        edit_flag = slug is not None or False
        post = None

        if edit_flag:
            post = models.CPost.objects.get_or_404(slug=slug)
            if not g.identity.can(editor_permission) and post.author.username != current_user.username:
                abort(404)

        display_slug = slug if slug else "slug_value"

        if not form:
            if post:
                post.post_id = str(post.id)
                post.tags_str = ", ".join(post.tags)
                form = forms.PostForm(obj=post)
            else:
                form = forms.PostForm(post_type=post_type)

        categories = models.CPost.objects.distinct("category")
        tags = models.CPost.objects.distinct("tags")

        context = {
            "edit_flag" : edit_flag,
            "form" : form,
            "display_slug" : display_slug,
            "categories" : categories,
            "tags" : tags,
            }
        return context

    def get(self, slug=None, form=None, post_type="post"):
        context = self.get_context(slug, form, post_type)
        return render_template(self.template_name, **context)

    def post(self, slug=None, post_type="post"):
        form = forms.PostForm(obj=request.form)
        if not form.validate():
            return self.get(slug, form)

        if slug:
            post = models.CPost.objects.get_or_404(slug=slug)
        else:
            post = models.CPost()
            post.author = get_current_user()

        post.title = form.title.data.strip()
        post.slug = form.slug.data.strip()
        post.raw = form.raw.data.strip()
        abstract = form.abstract.data.strip()
        post.abstract = abstract if abstract else post.raw[:140]
        post.category = form.category.data.strip() if form.category.data.strip() else None
        post.tags = [tag.strip() for tag in form.tags_str.data.split(",")] if form.tags_str.data else None
        post.post_type = form.post_type.data if form.post_type.data else None

        redirect_url = url_for("blog_admin.pages") if form.post_type.data == "page" else url_for("blog_admin.posts")

        if request.form.get("publish"):
            post.is_draft = False
            post.save()
            flash("Succeed to publish the {0}".format(post_type), "success")
            return redirect(redirect_url)
        if request.form.get("draft"):
            post.is_draft = True
            post.save()
            flash("Succeed to save the draft", "success")
            return redirect("{0}?draft=true".format(redirect_url))

        return self.get(slug, form)

    def delete(self, slug):
        post = models.CPost.object.get_or_404(slug=slug)
        post_type = post.post_type
        is_draft = post.is_draft
        post.delete()

        redirect_url = url_for("blog_admin.pages") if post_type == "page" else url_for("blog_admin.posts")

        if is_draft:
            redirect_url = redirect_url + "?draft=true"

        flash("Succeed to delete the {0}".format(post_type), "success")

        if request.args.get("ajax"):
            return "success"
        return redirect(redirect_url)


class SuPostsList(MethodView):
    decorators = [login_required, admin_permission.require(401)]
    template_name = 'blog_admin/su_posts.html'

    def get(self):
        posts = models.CPost.objects.all().order_by("-update_time")
        cur_type = request.args.get("type")
        if cur_type:
            posts = posts.filter(post_type=cur_type)
        cur_page = request.args.get("page", 1)
        if not cur_page:
            abort(404)

        posts = posts.paginate(page=int(cur_page), per_page=10)

        data = {
            "posts": posts,
            "post_types": POST_TYPES,
            "cut_type": cur_type,
        }
        return render_template(self.template_name, **data)

class SuPost(MethodView):
    decorators = [login_required, admin_permission.require(401)]
    template_name = 'blog_admin/su_post.html'

    def get_context(self, slug, form=None):
        post = models.CPost.objects.get_or_404(slug=slug)
        if not form:
            form = forms.SuPostFrom(obj=post)

        categories = models.CPost.objects.distinct("category")
        tags = models.CPost.objects.distinct("tags")

        context = {
            "form": form,
            "display_slug": slug,
            "post": post,
            "categories": categories,
            "tags": tags,
            "post_types": POST_TYPES,
        }

        return context

    def get(self, slug, form=None):
        context= self.get_context(slug, form)
        return render_template(self.template_name, **context)

    def post(self,slug):
        form = forms.SuPostFrom(request.form)
        if not form.validate():
            return self.get(slug, form)
        post = models.CPost.objects.get_or_404(slug=slug)
        post.title = form.title.data.strip()
        post.slug = form.slug.data.strip()
        post.fix_slug = form.fix_slug.data.strip()
        post.raw = form.raw.data.strip()
        abstract= form.abstract.data.strip()
        post.abstract = abstract if abstract else post.raw[:140]
        post.is_draft = form.is_draft.data
        post.author = form.author.data
        post.post_type = request.form.get("post_type") or post.post_type
        pub_time = request.form.get("publish_time")
        update_time = request.form.get("update_time")

        if pub_time:
            post.pub_time = datetime.datetime.strptime(pub_time, "%Y-%m-%d %H:%M:%S")

        if update_time:
            post.update_time = datetime.datetime.strptime(update_time, "%Y-%m-%d %H-%M-%S")

        redirect_url = url_for("blog_admin.su_posts")

        post.save(allow_set_time=True)

        flash("Succeed to update post", "success")

        return redirect(redirect_url)