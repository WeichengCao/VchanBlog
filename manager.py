# -*- coding: utf-8 -*-

import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask.ext.script import Manager, Server

from VchanBlog import create_app, db

app = create_app()
manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = '127.0.0.1',
    port = 5000)
)

if __name__ == "__main__":
    manager.run()

