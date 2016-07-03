# -*- coding: utf-8 -*-

from flask import current_app
from flask.ext.principal import Permission, RoleNeed, UserNeed, identity_loaded
from flask.ext.login import current_user


su_need = RoleNeed("su")
su_permission = Permission(su_need)
admin_permission = Permission(RoleNeed("admin")).union(su_permission)
editor_permission = Permission(RoleNeed("editor")).union(admin_permission)
writer_permission = Permission(RoleNeed("writer")).union(editor_permission)
reader_permission = Permission(RoleNeed("reader")).union(writer_permission)

@identity_loaded.connect
def on_identity_loaded(sender, identity):
    identity.user = current_user

    if hasattr(current_user, "username"):
        identity.provides.add(UserNeed(current_user.username))

    if hasattr(current_user, "role"):
        identity.provides.add(RoleNeed(current_user.role))

    if hasattr(current_user, "is_superuser") and current_user.is_superuser:
        identity.provides.add(su_need)

    identity.allow_edit = editor_permission.allows(identity)
    identity.allow_admin = admin_permission.allows(identity)
    identity.allow_write = admin_permission.allows(identity)