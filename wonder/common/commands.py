import os
from glob import glob
from flask.ext.script import Manager as Manager_
from flask.ext.script.commands import Server
from flask.ext.assets import ManageAssets


class Manager(Manager_):

    def __init__(self, app=None, assets_env=None, reloader_extra_files=None, **kwargs):
        super(Manager, self).__init__(app, **kwargs)

        if hasattr(reloader_extra_files, '__file__'):
            mod_path = os.path.dirname(reloader_extra_files.__file__)
            reloader_extra_files = glob(os.path.join(mod_path, '*.py'))

        self.add_command('runserver', Server(extra_files=reloader_extra_files))
        self.add_command('assets', ManageAssets(assets_env))
        self._cron_commands = {}

    def cron_command(self, interval=None):
        def decorator(f):
            self._cron_commands[f.__name__] = interval
            return self.command(f)
        return decorator

    def get_cron_commands(self):
        return self._cron_commands

    def handle(self, prog, args=None):
        return super(Manager, self).handle(prog, args)
