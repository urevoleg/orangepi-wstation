import time
import datetime as dt

from __init__ import app


def example(dt_now):
    """
    :param seconds:
    :return:
    """
    app.logger.info('Starting task')
    app.logger.debug(dt_now)
    app.logger.info('Task completed')


if __name__ == '__main__':
    import rq
    from redis import Redis
    from rq_scheduler import Scheduler
    # для корректной работы надо запустить rqscheduler -i 5

    q = rq.Queue('wstation', connection=Redis.from_url('redis://'))
    scheduler = Scheduler('wstation', connection=Redis.from_url('redis://'))

    scheduler.schedule(
        scheduled_time=dt.datetime.utcnow(),
        func='tasks.example',
        kwargs={'dt_now': dt.datetime.now()},
        interval=10,
        repeat=5,
    )

