# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import contextlib
import reframe as rfm

from hpctestlib.microbenchmarks.mpi.osu import build_osu_benchmarks, osu_build_run


class castorc_build_osu_benchmarks(build_osu_benchmarks):
    build_type = parameter(["cpu"])

    @run_after("init")
    def setup_modules(self):
        if self.build_type != "cuda":
            return

        if self.current_system.name in ("cyclone"):
            self.modules = ["CUDA/11.7.0"]
            self.build_system.ldflags = ["-L$EBROOTCUDA/lib64", "-lcudart", "-lcuda"]


class castorc_osu_benchmarks(osu_build_run):
    exclusive_access = True
    maintainers = ["cstyl"]
    tags = {"benchmark", "diagnostic", "maintenance"}


@rfm.simple_test
class castorc_osu_pt2pt_check(castorc_osu_benchmarks):
    valid_systems = ["cyclone:cpu"]
    valid_prog_environs = ["PrgEnv-gnu-nocuda"]
    benchmark_info = parameter(
        [("mpi.pt2pt.osu_bw", "bandwidth"), ("mpi.pt2pt.osu_latency", "latency")],
        fmt=lambda x: x[0],
        loggable=True,
    )
    osu_binaries = fixture(castorc_build_osu_benchmarks, scope="environment")
    allref = {
        "mpi.pt2pt.osu_bw": {
            "cpu": {
                "cyclone:cpu": {"bandwidth": (12329.94, -0.10, None, "MB/s")},
            },
        },
        "mpi.pt2pt.osu_latency": {
            "cpu": {
                "cyclone:cpu": {"latency": (0.98, None, 0.10, "us")},
            },
        },
    }

    @run_after("init")
    def setup_per_build_type(self):
        build_type = self.osu_binaries.build_type

        with contextlib.suppress(KeyError):
            self.reference = self.allref[self.benchmark_info[0]][build_type]


@rfm.simple_test
class castorc_osu_collective_check(castorc_osu_benchmarks):
    benchmark_info = parameter(
        [
            ("mpi.collective.osu_alltoall", "latency"),
            ("mpi.collective.osu_allreduce", "latency"),
        ],
        fmt=lambda x: x[0],
        loggable=True,
    )
    num_nodes = parameter([3, 6])
    extra_resources = {"switches": {"num_switches": 1}}
    valid_systems = ["cyclone:cpu"]
    valid_prog_environs = ["PrgEnv-gnu-nocuda"]
    osu_binaries = fixture(castorc_build_osu_benchmarks, scope="environment")
    allref = {
        "mpi.collective.osu_allreduce": {
            3: {"cyclone:cpu": {"latency": (2.79, None, 0.10, "us")}},
            6: {
                "cyclone:cpu": {"latency": (3.22, None, 0.10, "us")},
            },
        },
        "mpi.collective.osu_alltoall": {
            3: {
                "cyclone:cpu": {"latency": (1.77, None, 0.10, "us")},
            },
            6: {
                "cyclone:cpu": {"latency": (1.93, None, 0.10, "us")},
            },
        },
    }

    @run_after("init")
    def setup_by_scale(self):
        if self.osu_binaries.build_type == "cuda":
            # Filter out CUDA-aware versions
            self.valid_systems = []
            return

        self.num_tasks = self.num_nodes

        with contextlib.suppress(KeyError):
            self.reference = self.allref[self.benchmark_info[0]][self.num_nodes]
