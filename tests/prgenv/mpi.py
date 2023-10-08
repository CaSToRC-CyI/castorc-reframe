# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class MpiInitTest(rfm.RegressionTest):
    required_thread = parameter(["single", "funneled", "serialized", "multiple"])
    """This test checks the value returned by calling MPI_Init_thread.

    Output should look the same for every prgenv
    (mpi_thread_multiple seems to be not supported):

    # 'single':
    ['mpi_thread_supported=MPI_THREAD_SINGLE
      mpi_thread_queried=MPI_THREAD_SINGLE 0'],

    # 'funneled':
    ['mpi_thread_supported=MPI_THREAD_FUNNELED
      mpi_thread_queried=MPI_THREAD_FUNNELED 1'],

    # 'serialized':
    ['mpi_thread_supported=MPI_THREAD_SERIALIZED
      mpi_thread_queried=MPI_THREAD_SERIALIZED 2'],

    # 'multiple':
    ['mpi_thread_supported=MPI_THREAD_SERIALIZED
      mpi_thread_queried=MPI_THREAD_SERIALIZED 2']

    """

    def __init__(self, require_version=">=2.14.0"):
        self.valid_systems = ["cyclone:cpu"]
        self.valid_prog_environs = ["PrgEnv-gnu-nocuda", "PrgEnv-gnu", "PrgEnv-intel"]
        self.build_system = "SingleSource"
        self.sourcesdir = "src/mpi_thread"
        self.sourcepath = "mpi_init_thread.cpp"
        self.cppflags = {
            "single": ["-D_MPI_THREAD_SINGLE"],
            "funneled": ["-D_MPI_THREAD_FUNNELED"],
            "serialized": ["-D_MPI_THREAD_SERIALIZED"],
            "multiple": ["-D_MPI_THREAD_MULTIPLE"],
        }
        self.build_system.cppflags = self.cppflags[self.required_thread]
        self.time_limit = "1m"
        found_mpithread = sn.extractsingle(
            r"^mpi_thread_required=\w+\s+mpi_thread_supported=\w+"
            r"\s+mpi_thread_queried=\w+\s+(?P<result>\d)$",
            self.stdout,
            1,
            int,
        )
        self.mpithread_version = {
            "single": 0,
            "funneled": 1,
            "serialized": 2,
            "multiple": 3,
        }
        self.sanity_patterns = sn.all(
            [
                sn.assert_found(r"tid=0 out of 1 from rank 0 out of 1", self.stdout),
                sn.assert_eq(
                    found_mpithread, self.mpithread_version[self.required_thread]
                ),
            ]
        )

        self.maintainers = ["cstyl"]
        self.tags = {"diagnostic", "maintenance"}

    @run_before("run")
    def set_impi_env_variable(self):
        cs = self.current_system.name
        ce = self.current_environ.name

        if cs in ["cyclone"] and ce in ["PrgEnv-intel"]:
            # When using IntelMPI you first need to set the I_MPI_PMI_LIBRARY and then use srun
            self.env_vars["I_MPI_PMI_LIBRARY"] = "/usr/lib64/libpmi.so"


@rfm.simple_test
class MpiHelloTest(rfm.RegressionTest):
    def __init__(self):
        self.valid_systems = ["cyclone:cpu"]
        self.valid_prog_environs = ["PrgEnv-gnu-nocuda", "PrgEnv-gnu", "PrgEnv-intel"]

        self.descr = "MPI Hello World"
        self.sourcesdir = "src/mpi"
        self.sourcepath = "mpi_helloworld.c"
        self.num_tasks_per_node = 1
        self.num_tasks = 2
        self.time_limit = "1m"
        num_processes = sn.extractsingle(
            r"Received correct messages from (?P<nprocs>\d+) processes",
            self.stdout,
            "nprocs",
            int,
        )
        self.sanity_patterns = sn.assert_eq(num_processes, self.num_tasks_assigned - 1)

        self.maintainers = ["cstyl"]
        self.tags = {"diagnostic", "maintenance"}
        
    @run_before("run")
    def set_impi_env_variable(self):
        cs = self.current_system.name
        ce = self.current_environ.name

        if cs in ["cyclone"] and ce in ["PrgEnv-intel"]:
            # When using IntelMPI you first need to set the I_MPI_PMI_LIBRARY and then use srun
            self.env_vars["I_MPI_PMI_LIBRARY"] = "/usr/lib64/libpmi.so"

    @property
    @deferrable
    def num_tasks_assigned(self):
        return self.job.num_tasks
