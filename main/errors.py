# -*- coding: utf-8 -*-

from flask import render_template
from views import get_base_data

def page_not_found(e):
    data = get_base_data()
    return render_template("main/404.html", **data), 404

def handle_bad_request(e):
    return 'bad request', 400

def handle_forbidden(e):
    return render_template('blog_admin/403.html'), 403

def handle_unauthorized(e):
    return render_template('blog_admin/401.html'), 401

def admin_page_not_found(e):
    return render_template('blog_admin/404.html'), 404

def handle_unmatchable(*args, **kwargs):
    data = get_base_data()
    return render_template("main/404.html", **data), 404