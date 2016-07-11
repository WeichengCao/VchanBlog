# -*- coding: utf-8 -*-

import os

ROLES = (
    ('admin', 'admin'),
    ('editor', 'editor'),
    ('writer', 'writer'),
    ('reader', 'reader'),
)

SOCIAL_NETWORKS = {
    'weibo': {'fa_icon': 'fa fa-weibo', 'url': None},
    'weixin': {'fa_icon': 'fa fa-weixin', 'url': None},
    'twitter': {'fa_icon': 'fa fa fa-twitter', 'url': None},
    'github': {'fa_icon': 'fa fa-github', 'url': None},
    'facebook': {'fa_icon': 'fa fa-facebook', 'url': None},
    'linkedin': {'fa_icon': 'fa fa-linkedin', 'url': None},
}

PER_PAGE = 10
ARCHIVE_PER_PAGE = 10
POST_TYPES = ('post', 'page')

VchanBlogSettings = {
    'post_types': ('post', 'page'),
    'allow_registration': os.environ.get('allow_registration', 'true').lower() == 'true',
    'allow_su_creation': os.environ.get('allow_su_creation', 'true').lower() == 'true',
    'allow_donate': os.environ.get('allow_donate', 'false').lower() == 'true',
    'auto_role': os.environ.get('auto_role', 'reader').lower(),
    'blog_meta': {
        'name': os.environ.get('name').decode('utf8') if os.environ.get('name') else 'VChan Blog',
        'subtitle': os.environ.get('subtitle').decode('utf8') if os.environ.get('subtitle') else 'Python Learning',
        'description': os.environ.get('description').decode('utf8') if os.environ.get('description') else 'VChan Blog Description',
        'owner': os.environ.get('owner').decode('utf8') if os.environ.get('owner') else 'VChan',
        'keywords': os.environ.get('keywords').decode('utf8') if os.environ.get('keywords') else 'python,django,flask,docker,MongoDB',
        'google_site_verification': os.environ.get('google_site_verification') or '12345678',
        'baidu_site_verification': os.environ.get('baidu_site_verification') or '87654321',
    },
    'pagination':{
        'per_page': int(os.environ.get('per_page', 5)),
        'admin_per_page': int(os.environ.get('admin_per_page', 10)),
        'archive_per_page': int(os.environ.get('admin_per_page', 20)),
    },
    'blog_comment':{
        'allow_comment': os.environ.get('allow_comment', 'true').lower() == 'true',
        'comment_type': os.environ.get('comment_type', 'duoshuo').lower(),
        'comment_opt':{
            'duoshuo': 'VChan-blog', # shotname of duoshuo
            }
    },
    'donation': {
        'allow_donate': os.environ.get('allow_donate', 'false').lower() == 'true',
        'donation_msg': os.environ.get('donation_msg', 'You can donate to me if the article makes sense to you')
    },
    'allow_share_article': os.environ.get('allow_share_article', 'true').lower() == 'true',

}

class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    MONGODB_SETTINGS = {'DB': 'VChanBlog'}
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fjdljLJDL08_80jflKzcznv*c'

    TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates').replace('\\', '/')
    STATIC_PATH = os.path.join(BASE_DIR, 'static').replace('\\', '/')


    @staticmethod
    def init_app(app):
        pass

class DevConfig(Config):
    DEBUG = True
