from oar.kao.scheduling import schedule_id_jobs_ct, set_slots_with_prev_scheduled_jobs
from oar.kao.slot import Slot, SlotSet
from oar.lib.job_handling import JobPseudo
from oar.lib.plugins import find_plugin_function
from procset import ProcSet

ASSIGN_ENTRY_POINTS = "oar.assign_func"
FIND_ENTRY_POINTS = "oar.find_func"


def set_assign_func(job, name):

    job.assign = True
    job.assign_func = find_plugin_function(ASSIGN_ENTRY_POINTS, name)


def set_find_func(job, name):

    job.find = True
    job.find_func = find_plugin_function(FIND_ENTRY_POINTS, name)


def compare_slots_val_ref(slots, v):
    sid = 1
    i = 0
    while True:
        slot = slots[sid]
        (b, e, itvs) = v[i]
        if (slot.b != b) or (slot.e != e) or not (slot.itvs == itvs):
            return False
        sid = slot.next
        if sid == 0:
            break
        i += 1
    return True


def test_assign_round_robin():

    v = [(0, 100, ProcSet(*[(1, 16), (25, 32)]))]

    res = ProcSet(*[(1, 32)])
    ss = SlotSet(Slot(1, 0, 0, ProcSet(*[(1, 16), (25, 32)]), 0, 100))
    all_ss = {"default": ss}
    hy = {"node": [ProcSet(*x) for x in [[(1, 8)], [(9, 16)], [(17, 24)], [(25, 32)]]]}

    j3 = JobPseudo(
        id=3,
        types={},
        deps=[],
        key_cache={},
        mld_res_rqts=[(1, 60, [([("node", 1)], res)])],
    )

    set_assign_func(j3, "round_robin")

    schedule_id_jobs_ct(
        all_ss,
        {3: j3},
        hy,
        [3],
        20,
    )

    assert compare_slots_val_ref(ss.slots, v) is True
