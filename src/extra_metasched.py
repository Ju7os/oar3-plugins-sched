# coding: utf-8
"""Extra metascheduling functions which can be called between each queue handling"""

from oar.lib.globals import get_logger, init_config
from oar.lib.models import Resource

config = init_config()
logger = get_logger("oar-plugins.custom_extra_metasched")


def extra_metasched_default(
    db_session,
    prev_queue,
    plt,
    scheduled_jobs,
    all_slot_sets,
    job_security_time,
    queue,
    initial_time_sec,
    extra_metasched_config,
):
    logger.info("plugin successfully called ;)")
    pass


def extra_metasched_logger(
    db_session,
    prev_queue,
    plt,
    scheduled_jobs,
    all_slot_sets,
    job_security_time,
    queue,
    initial_time_sec,
    extra_metasched_config,
):
    logger.info("plugin successfully called ;)")


def extra_metasched_foo(
    db_session,
    prev_queue,
    plt,
    scheduled_jobs,
    all_slot_sets,
    job_security_time,
    queue,
    initial_time_sec,
    extra_metasched_config,
):

    if prev_queue is None:
        # set first resource deployable
        first_id = db_session.query(Resource).first().id
        db_session.query(Resource).filter(Resource.id == first_id).update(
            {Resource.deploy: "YES"}, synchronize_session=False
        )
        db_session.commit()
