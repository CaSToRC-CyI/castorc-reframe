# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import re
import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.logging import getlogger


class HelloWorldBaseTest(rfm.RegressionTest):
    lang = parameter(["c", "cpp", "f90"])
    prgenv_flags = {}
    sourcepath = "hello_world"
    build_system = "SingleSource"
    prebuild_cmds = ['_rfm_build_time="$(date +%s%N)"']
    postbuild_cmds = [
        '_rfm_build_time="$(($(date +%s%N)-_rfm_build_time))"',
        'echo "Compilations time (ns): $_rfm_build_time"',
    ]
    # valid_systems = ["cyclone:login", "cyclone:cpu", "cyclone:gpu"]
    valid_systems = ["cyclone:login", "cyclone:cpu"]
    valid_prog_environs = ["*"]
    reference = {"*": {"compilation_time": (60, None, 0.1, "s")}}
    exclusive_access = True

    maintainers = ["cstyl"]
    tags = {"diagnostic", "maintenance"}

    @run_after("init")
    def set_description(self):
        lang_names = {"c": "C", "cpp": "C++", "f90": "Fortran 90"}
        self.descr = f"{lang_names[self.lang]} Hello, World"

    @run_before("compile")
    def prepare_build(self):
        envname = re.sub(
            r"(PrgEnv-\w+).*", lambda m: m.group(1), self.current_environ.name
        )
        try:
            prgenv_flags = self.prgenv_flags[envname]
        except KeyError:
            prgenv_flags = []

        self.build_system.cflags = prgenv_flags
        self.build_system.cxxflags = prgenv_flags
        self.build_system.fflags = prgenv_flags

    @sanity_function
    def assert_hello_world(self):
        result = sn.findall(
            r"Hello, World from thread \s*(\d+) out "
            r"of \s*(\d+) from process \s*(\d+) out of "
            r"\s*(\d+)",
            self.stdout,
        )

        num_tasks = sn.getattr(self, "num_tasks")
        num_cpus_per_task = sn.getattr(self, "num_cpus_per_task")

        def tid(match):
            return int(match.group(1))

        def num_threads(match):
            return int(match.group(2))

        def rank(match):
            return int(match.group(3))

        def num_ranks(match):
            return int(match.group(4))

        return sn.all(
            sn.chain(
                [sn.assert_eq(sn.count(result), num_tasks * num_cpus_per_task)],
                sn.map(lambda x: sn.assert_lt(tid(x), num_threads(x)), result),
                sn.map(lambda x: sn.assert_lt(rank(x), num_ranks(x)), result),
                sn.map(lambda x: sn.assert_lt(tid(x), num_cpus_per_task), result),
                sn.map(
                    lambda x: sn.assert_eq(num_threads(x), num_cpus_per_task), result
                ),
                sn.map(lambda x: sn.assert_lt(rank(x), num_tasks), result),
                sn.map(lambda x: sn.assert_eq(num_ranks(x), num_tasks), result),
            )
        )

    @performance_function("s")
    def compilation_time(self):
        return (
            sn.extractsingle(
                r"Compilations time \(ns\): (\d+)", self.build_stdout, 1, float
            )
            * 1.0e-9
        )


@rfm.simple_test
class HelloWorldTestSerial(HelloWorldBaseTest):
    sourcesdir = "src/serial"
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1

    maintainers = ["cstyl"]
    tags = {"diagnostic", "maintenance"}

    @run_after("init")
    def update_description(self):
        self.descr += " Serial "

    # @run_after("setup")
    # def extend_valid_prog_environs(self):
    #     cs = self.current_system.name
    #     cp = self.current_partition.name

    #     print(f"System = {cs} and Partition = {cp}")
    #     # if cs in ["cyclone"] and cp in ["gpu", "login"]:
    #     if cs in ["cyclone"] and cp in ["login"]:
    #         self.valid_prog_environs += [
    #             "PrgEnv-gnu-nompi",
    #             "PrgEnv-gnu",
    #         ]
    #         print(self.valid_prog_environs)

    @run_after("setup")
    def set_ngpus(self):
        cs = self.current_system.name
        cp = self.current_partition.name

        if cs in ["cyclone"] and cp in ["gpu"]:
            self.extra_resources = {"gres": {"num_gpus_per_node": "1"}}

    @run_before("compile")
    def update_sourcepath(self):
        self.sourcepath += f"_serial.{self.lang}"


@rfm.simple_test
class HelloWorldTestOpenMP(HelloWorldBaseTest):
    sourcesdir = "src/openmp"
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 4

    maintainers = ["cstyl"]
    tags = {"diagnostic", "maintenance"}

    @run_after("init")
    def set_prgenv_compilation_flags_map(self):
        self.prgenv_flags = {
            "PrgEnv-gnu": ["-fopenmp"],
            "PrgEnv-nvidia": [
                "-fopenmp" if self.lang == "f90" else "-Xcompiler -fopenmp"
            ],
            "PrgEnv-gnu-nompi-nocuda": ["-fopenmp"],
            "PrgEnv-gnu-nocuda": ["-fopenmp"],
            "PrgEnv-intel-nompi": ["-qopenmp"],
            "PrgEnv-intel": ["-qopenmp"],
        }

    @run_after("init")
    def update_description(self):
        self.descr += " OpenMP "

    @run_before("compile")
    def update_sourcepath(self):
        self.sourcepath += "_openmp." + self.lang

    @run_before("run")
    def set_omp_env_variable(self):
        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.env_vars["OMP_NUM_THREADS"] = self.num_cpus_per_task


@rfm.simple_test
class HelloWorldTestMPI(HelloWorldBaseTest):
    sourcesdir = "src/mpi"
    # for the MPI test the self.num_tasks_per_node should always be one. If
    # not, the test will fail for the total number of lines in the output
    # file is different then self.num_tasks * self.num_tasks_per_node
    num_tasks = 2
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    valid_systems = ["cyclone:cpu"]
    valid_prog_environs = ["PrgEnv-gnu-nocuda", "PrgEnv-gnu", "PrgEnv-intel"]

    maintainers = ["cstyl"]
    tags = {"diagnostic", "maintenance"}

    @run_after("init")
    def update_description(self):
        self.descr += " MPI "

    @run_before("compile")
    def update_sourcepath(self):
        self.sourcepath += "_mpi." + self.lang

    @run_before("run")
    def set_impi_env_variable(self):
        cs = self.current_system.name
        ce = self.current_environ.name

        if cs in ["cyclone"] and ce in ["PrgEnv-intel"]:
            # When using IntelMPI you first need to set the I_MPI_PMI_LIBRARY and then use srun
            self.env_vars["I_MPI_PMI_LIBRARY"] = "/usr/lib64/libpmi.so"


@rfm.simple_test
class HelloWorldTestMPIOpenMP(HelloWorldBaseTest):
    sourcesdir = "src/mpi_openmp"
    num_tasks = 6
    num_tasks_per_node = 3
    num_cpus_per_task = 4
    valid_systems = ["cyclone:cpu"]
    valid_prog_environs = ["PrgEnv-gnu-nocuda", "PrgEnv-gnu", "PrgEnv-intel"]

    maintainers = ["cstyl"]
    tags = {"diagnostic", "maintenance"}
    
    @run_after("init")
    def set_prgenv_compilation_flags_map(self):
        self.prgenv_flags = {
            "PrgEnv-gnu": ["-fopenmp"],
            "PrgEnv-gnu-nocuda": ["-fopenmp"],
            "PrgEnv-intel": ["-qopenmp"],
        }

    @run_after("init")
    def update_description(self):
        self.descr += " MPI + OpenMP "

    @run_before("compile")
    def update_sourcepath(self):
        self.sourcepath += "_mpi_openmp." + self.lang

    @run_before("run")
    def set_omp_env_variable(self):
        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.env_vars["OMP_NUM_THREADS"] = self.num_cpus_per_task

    @run_before("run")
    def set_impi_env_variable(self):
        cs = self.current_system.name
        ce = self.current_environ.name

        if cs in ["cyclone"] and ce in ["PrgEnv-intel"]:
            # When using IntelMPI you first need to set the I_MPI_PMI_LIBRARY and then use srun
            self.env_vars["I_MPI_PMI_LIBRARY"] = "/usr/lib64/libpmi.so"
