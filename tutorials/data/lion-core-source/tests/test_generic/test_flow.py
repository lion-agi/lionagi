import pytest
from lionabc.exceptions import LionIDError

from lion_core.generic.component import Component
from lion_core.generic.flow import Flow
from lion_core.generic.progression import progression
from lion_core.sys_utils import SysUtil

sample_progressions = [
    progression([Component(content=i) for i in range(3)], f"prog_{j}")
    for j in range(3)
]

sample_flow = Flow(progressions=sample_progressions, default_name="main")


def test_flow_with_generator_input():
    def gen_progressions():
        for i in range(5):
            yield progression(
                [Component(content=j) for j in range(i)], f"gen_prog_{i}"
            )

    gen_flow = Flow(progressions=list(gen_progressions()))
    assert len(gen_flow) == 5
    assert gen_flow.get("gen_prog_4").size() == 4


@pytest.mark.parametrize(
    "n_progs, prog_size", [(10, 100), (100, 10), (1000, 1)]
)
def test_flow_performance_scaling(n_progs, prog_size):
    import random
    import time

    start_time = time.time()

    large_flow = Flow(
        progressions=[
            progression(
                [Component(content=i) for i in range(prog_size)],
                f"perf_prog_{j}",
            )
            for j in range(n_progs)
        ]
    )

    creation_time = time.time() - start_time

    start_time = time.time()
    for _ in range(100):
        random_prog = random.choice(list(large_flow.keys()))
        _ = large_flow[random_prog]

    access_time = time.time() - start_time

    assert creation_time < 2.0  # Adjusted for larger scale
    assert access_time < 0.5  # Adjusted for larger scale


@pytest.mark.parametrize("op", ["union", "intersection", "difference"])
def test_flow_set_operations(op):
    flow1 = Flow(
        [progression([Component(content=i) for i in range(5)], "set_op_1")]
    )
    flow2 = Flow(
        [progression([Component(content=i) for i in range(3, 8)], "set_op_2")]
    )

    if op == "union":
        result = Flow(
            [
                progression(
                    set(flow1["set_op_1"]) | set(flow2["set_op_2"]),
                    "union",
                )
            ]
        )
        assert result["union"].size() == 10
    elif op == "intersection":
        result = Flow(
            [
                progression(
                    set(flow1["set_op_1"]) & set(flow2["set_op_2"]),
                    "intersection",
                )
            ]
        )
        assert result["intersection"].size() == 0
    elif op == "difference":
        result = Flow(
            [
                progression(
                    set(flow1["set_op_1"]) - set(flow2["set_op_2"]),
                    "difference",
                )
            ]
        )
        assert result["difference"].size() == 5


def test_sys_util_get_id_with_elements():
    element = Component(content=42)
    assert SysUtil.get_id(element) == element.ln_id


def test_sys_util_get_id_with_invalid_input():
    with pytest.raises(LionIDError):
        SysUtil.get_id("not_a_valid_id")


def test_flow_with_proper_id_handling():
    flow = Flow(
        progressions=[
            progression([], "test_prog_1"),
            progression([], "test_prog_2"),
        ]
    )
    assert SysUtil.is_id(flow.registry["test_prog_1"])
    assert SysUtil.is_id(flow.registry["test_prog_2"])


def test_flow_add_element_with_id():
    flow = Flow([progression([], "test_prog")])
    element = Component(content=100)
    flow.append(element, "test_prog")
    assert SysUtil.get_id(element) in flow["test_prog"].order


# File: tests/test_flow_extended.py
