# -*- coding: utf-8 -*-

from defines import *
from urlparse import urljoin
from flask import request, render_template, abort, current_app, make_response
from flask_login import current_user
from werkzeug.contrib.atom import AtomFeed
from mongoengine.queryset.visitor import Q

import models
import datetime


def get_base_data():
    pages = models.CPost.objects.filter(post_type="page", is_draft=False)
    blog_meta = VchanBlogSettings["blog_meta"]
    data = {"blog_meta":blog_meta,
            "pages":pages,}
    return data

def list_posts():
    posts = models.CPost.objects.filter(post_type="post", is_draft=False).order_by("-pub_time")
    tags = posts.distinct('tags')

    cur_category = request.args.get('category')
    cur_tag = request.args.get('tag')
    cur_page = request.args.get('page', 1)
    keywords = request.args.get('keywords')

    if keywords:
        # posts = posts.filter(raw__contains=keywords )
        posts = posts.filter(Q(raw__contains=keywords) | Q(title__contains=keywords))

    if cur_category:
        posts = posts.filter(category=cur_category)

    if cur_tag:
        posts = posts.filter(tags=cur_tag)

    posts = posts.paginate(page=int(cur_page), per_page=PER_PAGE)

    #group by aggregate
    category_cursor = models.CPost._get_collection().aggregate([
            { '$group' :
                { '_id' : {'category' : '$category' },
                  'name' : { '$first' : '$category' },
                  'count' : { '$sum' : 1 },
                }
            }
        ])

    data = get_base_data()
    data['posts'] = posts
    data['cur_category'] = cur_category
    data['category_cursor'] = category_cursor
    data['cur_tag'] = cur_tag
    data['tags'] = tags
    data['keywords'] = keywords
    return render_template('main/index.html', **data)

def recent_feed():
    feed = AtomFeed('Recent Articles', feed_url=request.url, url=request.url_root)

    posts = models.CPost.objects.filter(post_type='post', is_draft=False)[:15]
    for post in posts:
        # return post.get_absolute_url()
        feed.add(post.title, unicode(post.content_html),
                 content_type='html',
                 author=post.author.username,
                 url=make_external(post.get_absolute_url()),
                 updated=post.update_time,
                 published=post.pub_time)
    return feed.get_response()

def make_external(url):
    return urljoin(request.url_root, url)

def archive():
    posts = models.CPost.objects.filter(post_type='post', is_draft=False).order_by('-pub_time')

    cur_category = request.args.get('category')
    cur_tag = request.args.get('tag')
    cur_page = request.args.get('page', 1)

    if cur_category:
        posts = posts.filter(category=cur_category)

    if cur_tag:
        posts = posts.filter(tags=cur_tag)

    posts = posts.paginate(page=int(cur_page), per_page=ARCHIVE_PER_PAGE)

    data = get_base_data()
    data['posts'] = posts

    return render_template('main/archive.html', **data)

def post_detail(slug, post_type='post', fix=False):
    post = models.CPost.objects.get_or_404(slug=slug, post_type=post_type) if not fix \
        else models.CPost.objects.get_or_404(fix_slug=slug, post_type=post_type)

    if post.is_draft and current_user.isanonymous:
        abort(404)

    data = get_base_data()

    data_ext = {
        "post": post,
        "allow_donate": VchanBlogSettings["donation"]["allow_donate"],
        "donation_msg": VchanBlogSettings["donation"]["donation_msg"],
        "allow_comment": VchanBlogSettings["blog_comment"]["allow_comment"],
        "allow_share_article": VchanBlogSettings["allow_share_article"],
    }

    data.update(data_ext)

    if data["allow_comment"]:
        comment_type = VchanBlogSettings["blog_comment"]["comment_type"]
        comment_shortname = VchanBlogSettings["blog_comment"]["comment_opt"]["duoshuo"]
        comment_func = get_comment_func(comment_type)
        data["comment_html"] = comment_func(comment_shortname, slug, post.title, request.base_url) if comment_func else ""

    return render_template("main/post.html", **data)

def get_comment_func(comment_type):
    if comment_type == 'duoshuo':
        return duoshuo_comment
    else:
        return None

def duoshuo_comment(duoshuo_shortname, post_id, post_title, post_url):
    template_name = "main/misc/duoshuo.html"
    data = {
        "duoshuo_shortname": duoshuo_shortname,
        "post_id": post_id,
        "post_title": post_title,
        "post_url": post_url,
    }

    return render_template(template_name, **data)

def author_detail(username):
    author = models.CUser.objects.get_or_404(username=username)
    posts = models.CPost.objects.filter(post_type="post", is_draft=False, author=author).order_by("-pub_time")
    cur_page = request.args.get("page",1)
    posts = posts.paginate(page=int(cur_page), per_page=10)

    data = get_base_data()
    data["user"] = author
    data["posts"] = posts

    return render_template('main/author.html', **data)

def sitemap():
    pages = []
    ten_days_ago = (datetime.now() - datetime.timedelta(days=10)).date().isoformat()

    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments)==0:
            pages.append([rule.rule, ten_days_ago])

    posts = models.CPost.objects.filter(is_draft=False, post_type="post")
    for post in posts:
        pages.append((post.get_absolute_url(), post.update_time.date().isoformat()))

    blog_pages = models.CPost.objects.filter(is_draft=False, post_type="page")
    for page in blog_pages:
        pages.append((page.get_absolute_url(), page.update_time.date().isoformat()))

    sitemap_xml = render_template("main/sitemap.xml", pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response
