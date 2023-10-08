# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class AllocSpeedTest(rfm.RegressionTest):
    sourcepath = "alloc_speed.cpp"
    valid_systems = ["cyclone:cpu"]
    valid_prog_environs = ["PrgEnv-gnu-nocuda"]
    build_system = "SingleSource"
    exclusive_access = True

    maintainers = ["cstyl"]
    tags = {"benchmark", "diagnostic", "maintenance"}

    reference = {
        "cyclone:cpu": {"time": (0.29, None, 0.15, "s")},
    }

    @run_after("init")
    def set_descr(self):
        self.descr = f"Time to allocate 4096 MB"

    @run_before("compile")
    def set_cxxflags(self):
        self.build_system.cxxflags = ["-O3", "-std=c++11"]

    @sanity_function
    def assert_4GB(self):
        return sn.assert_found("4096 MB", self.stdout)

    @performance_function("s")
    def time(self):
        return sn.extractsingle(
            r"4096 MB, allocation time (?P<time>\S+)", self.stdout, "time", float
        )
