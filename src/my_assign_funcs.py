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

    resource_available_not_found = 0
    slots = slot_set.slots
    result_start_time = slots[1].b
    result_resource_available = ProcSet()
    result_resource_request = ProcSet()
    result_slot_id_left = 0
    result_slot_id_right = 0

    for resource_request in job.mld_res_rqts:
        _, walltime, _ = resource_request
        resource_available, slot_id_left, _ = find_first_suitable_contiguous_slots(
            slot_set, job, resource_request, hy, min_start_time
        )
        if len(resource_available) == 0:
            resource_available_not_found += 1
            continue

        if hy["node"][job.id % nb_ressources_max].issubset(resource_available):
            result_start_time = slots[slot_id_left].b
            result_resource_available = resource_available
            result_resource_request = resource_request
            (result_slot_id_left, result_slot_id_right) = (
                slot_set.get_encompassing_slots(
                    result_start_time, slots[slot_id_left].b + walltime
                )
            )
        else:
            resource_available_not_found += 1

    if resource_available_not_found == len(job.mld_res_rqts):
        logger.info(f"cannot schedule job {job.id}")
        job.res_set = ProcSet()
        job.start_time = -1
        job.moldable_id = -1
        return

    (moldable_id, walltime, _) = result_resource_request
    job.moldable_id = moldable_id
    job.res_set = result_resource_available
    job.start_time = result_start_time
    job.walltime = walltime

    slot_set.split_slots(result_slot_id_left, result_slot_id_right, job)
    return result_slot_id_left, result_slot_id_right, job
