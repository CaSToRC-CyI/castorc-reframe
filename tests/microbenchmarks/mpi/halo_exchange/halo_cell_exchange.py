# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HaloCellExchangeTest(rfm.RegressionTest):
    def __init__(self):
        self.sourcepath = "halo_cell_exchange.c"
        self.build_system = "SingleSource"
        self.build_system.cflags = ["-O2"]
        self.valid_systems = ["cyclone:cpu"]
        self.valid_prog_environs = ["PrgEnv-gnu-nocuda"]
        self.num_tasks = 6
        self.num_tasks_per_node = 1
        self.num_gpus_per_node = 0

        self.executable_opts = ["input.txt"]

        self.sanity_patterns = sn.assert_eq(
            sn.count(sn.findall(r"halo_cell_exchange", self.stdout)), 9
        )

        self.perf_patterns = {
            "time_2_10": sn.extractsingle(
                r"halo_cell_exchange 6 2 1 1 10 10 10" r" \S+ (?P<time_mpi>\S+)",
                self.stdout,
                "time_mpi",
                float,
            ),
            "time_2_10000": sn.extractsingle(
                r"halo_cell_exchange 6 2 1 1 10000 10000 10000"
                r" \S+ (?P<time_mpi>\S+)",
                self.stdout,
                "time_mpi",
                float,
            ),
            "time_2_1000000": sn.extractsingle(
                r"halo_cell_exchange 6 2 1 1 1000000 1000000 1000000"
                r" \S+ (?P<time_mpi>\S+)",
                self.stdout,
                "time_mpi",
                float,
            ),
            "time_4_10": sn.extractsingle(
                r"halo_cell_exchange 6 2 2 1 10 10 10" r" \S+ (?P<time_mpi>\S+)",
                self.stdout,
                "time_mpi",
                float,
            ),
            "time_4_10000": sn.extractsingle(
                r"halo_cell_exchange 6 2 2 1 10000 10000 10000"
                r" \S+ (?P<time_mpi>\S+)",
                self.stdout,
                "time_mpi",
                float,
            ),
            "time_4_1000000": sn.extractsingle(
                r"halo_cell_exchange 6 2 2 1 1000000 1000000 1000000"
                r" \S+ (?P<time_mpi>\S+)",
                self.stdout,
                "time_mpi",
                float,
            ),
            "time_6_10": sn.extractsingle(
                r"halo_cell_exchange 6 3 2 1 10 10 10" r" \S+ (?P<time_mpi>\S+)",
                self.stdout,
                "time_mpi",
                float,
            ),
            "time_6_10000": sn.extractsingle(
                r"halo_cell_exchange 6 3 2 1 10000 10000 10000"
                r" \S+ (?P<time_mpi>\S+)",
                self.stdout,
                "time_mpi",
                float,
            ),
            "time_6_1000000": sn.extractsingle(
                r"halo_cell_exchange 6 3 2 1 1000000 1000000 1000000"
                r" \S+ (?P<time_mpi>\S+)",
                self.stdout,
                "time_mpi",
                float,
            ),
        }

        self.reference = {
            "cyclone:cpu": {
                "time_2_10": (1.640666e-06, None, 0.50, "s"),
                "time_2_10000": (1.247299e-05, None, 0.50, "s"),
                "time_2_1000000": (3.311696e-04, None, 0.50, "s"),
                "time_4_10": (2.003486e-06, None, 0.50, "s"),
                "time_4_10000": (1.315197e-05, None, 0.50, "s"),
                "time_4_1000000": (4.385816e-04, None, 0.50, "s"),
                "time_6_10": (2.015788e-06, None, 0.50, "s"),
                "time_6_10000": (1.309701e-05, None, 0.50, "s"),
                "time_6_1000000": (4.473129e-04, None, 0.50, "s"),
            },
        }

        self.strict_check = False

        self.maintainers = ["cstyl"]
        self.tags = {"benchmark", "diagnostic", "maintenance"}
