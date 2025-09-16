from oar.kao.scheduling import find_resource_hierarchies_job, intersec_itvs_slots
from oar.kao.slot import SlotSet
from oar.lib.globals import get_logger, init_config
from oar.lib.job_handling import ALLOW
from oar.lib.models import Job
from procset import ProcSet

config = init_config()
logger = get_logger("oar-plugs.my_assign_funcs", forward_stderr=True)


def find_round_robing(slot_set: SlotSet, job: Job, hierarchy, min_start_time):

    (_, walltime, hierarchy_resource_requests) = job.mld_res_rqts[0]

    itvs = ProcSet()

    slots = slot_set.slots

    slot_id_left = slot_set.first().id
    slot_id_left = slot_set.slot_id_at(min_start_time)

    slot_id_right = slot_id_left
    for slot_begin, slot_end in slot_set.traverse_with_width(
        walltime, start_id=slot_id_left
    ):
        slot_id_left = slot_begin.id
        slot_id_right = slot_end.id

        itvs_avail = intersec_itvs_slots(slots, slot_begin.id, slot_end.id)

        for hierarchy_resource_request in hierarchy_resource_requests:
            hierarchy_resource_request = (
                hierarchy_resource_request[0],
                ProcSet(job.id % 8),
            )

        itvs = find_resource_hierarchies_job(
            itvs_avail, [([("resource_id", 1)], ProcSet(job.id % 8))], hierarchy
        )

        if len(itvs) != 0:
            break

    if len(itvs) == 0:
        return (ProcSet(), -1, -1)
    else:
        return (itvs, slot_id_left, slot_id_right)


def assign_round_robin(slot_set: SlotSet, job: Job, hy, min_start_time):

    with open("/tmp/oar-plug.log", "w") as file:
        file.write(
            f"Job: {job.id}, Hierarchy: {hy}, Resource_request: {job.mld_res_rqts[0]}, Slot_Set: {slot_set}"
        )
        slots = slot_set.slots

        resource_request = job.mld_res_rqts[0]
        _, walltime, _ = resource_request
        resource_available, slot_id_left, slot_id_right = find_round_robing(
            slot_set, job, hy, min_start_time
        )
        file.write(
            f"Resource_available: {resource_available}, slot_id_left: {slot_id_left}, slot_id_right: {slot_id_right}"
        )

        if slot_id_left != -1:
            result_start_time = slots[slot_id_left].b
            result_resource_available = resource_available
            result_resource_request = resource_request
            (result_slot_id_left, result_slot_id_right) = (
                slot_set.get_encompassing_slots(
                    result_start_time, slots[slot_id_left].b + walltime
                )
            )
        else:
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
