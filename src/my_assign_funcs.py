# coding: utf-8
import copy
import pickle

from oar.kao.scheduling import (
    find_first_suitable_contiguous_slots,
    find_resource_hierarchies_job,
)
from oar.kao.slot import Slot, SlotSet
from oar.lib.globals import get_logger, init_config
from oar.lib.hierarchy import extract_n_scattered_block_itv
from oar.lib.models import Job, Resource
from procset import ProcInt, ProcSet

config = init_config()
logger = get_logger("oar-plugs.custom_scheduling")

nb_ressources_max = 8


def assign_round_robin(slot_set: SlotSet, job: Job, hy, min_start_time):
    resource_id = job.id % nb_ressources_max
    requested_itvs = ProcSet(resource_id)

    mld_id, walltime, _ = requested_itvs
    (
        res_set,
        sid_left,
        sid_right,
    ) = find_first_suitable_contiguous_slots(
        slot_set, job, requested_itvs, hy, min_start_time
    )
    if len(res_set) == 0:
        logger.info(f"cannot schedule job {job.id}")
        job.res_set = ProcSet()
        job.start_time = -1
        job.moldable_id = -1
        return

    job.moldable_id = mld_id
    job.res_set = res_set
    job.start_time = start_time
    job.walltime = walltime

    slot_set.split_slots(sid_left, sid_right, job)
    return sid_left, sid_right, job
