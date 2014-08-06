import os
import sys
import time
import signal
from datetime import datetime, timedelta
from sqlalchemy import func
from flask import Flask, current_app
from .timing import record_timing


def hup_handler(sighup, frame):
    global _hup_received
    _hup_received = True
_hup_received = False


class MuleRunner(object):

    lock_file = None
    sleep_interval = None

    app = None

    def __init__(self, app=None):
        if app:
            self.app = app

    def setup(self):
        # Catch HUP from uwsgi
        signal.signal(signal.SIGHUP, hup_handler)
        return current_app or (self.app if isinstance(self.app, Flask) else self.app())

    def run(self):
        app = self.setup()

        while True:
            if self.lock_file and os.path.exists(self.lock_file):
                time.sleep(10)
            else:
                with app.app_context():
                    success = self.poll()
                if self.sleep_interval and not success and not _hup_received:
                    time.sleep(self.sleep_interval)
            if _hup_received:
                sys.exit()


def _pg_lock(db, lock, f):
    query = 'select %s(%d);' % (f, hash(lock))
    return db.session.execute(query).fetchone()[0]
lock_command = lambda session, command: _pg_lock(session, command, 'pg_try_advisory_lock')
unlock_command = lambda session, command: _pg_lock(session, command, 'pg_advisory_unlock')


class CronProcessor(MuleRunner):
    sleep_interval = 10

    def __init__(self, db, manager, job_control, *args, **kwargs):
        super(CronProcessor, self).__init__(*args, **kwargs)
        if db:
            self.db = db
        if manager:
            self.manager = manager
        if job_control:
            self.job_control = job_control

    def poll(self):
        cron_commands = self.manager.get_cron_commands()
        enabled_jobs = set(cron_commands.keys()) -\
            set(current_app.config.get('DISABLED_CRON_JOBS', []))
        command = self.job_control.query.filter(
            self.job_control.next_run <= func.now(),
            self.job_control.job.in_(enabled_jobs),
        ).order_by(func.random()).limit(1).value('job')   # random used to avoid getting stuck on long running jobs
        if not command:
            return

        acquired = lock_command(self.db, command)
        if not acquired:
            # somebody else is processing this job
            return

        start_time = time.time()
        try:
            self.manager.handle('cron', [command])
        except Exception:
            current_app.logger.exception('Failed to run command: %s', command)
            success = False
        else:
            self.job_control.query.filter_by(job=command).update(
                {'next_run': datetime.now() + timedelta(seconds=cron_commands[command])})
            self.job_control.query.session.commit()
            success = True
        finally:
            assert unlock_command(self.db, command)

        record_timing('cron_processor.%s.run_time' % command, time.time() - start_time)

        return success
