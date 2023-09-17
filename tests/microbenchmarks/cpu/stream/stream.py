# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class StreamTest(rfm.RegressionTest):
    '''This test checks the stream test:
       Function    Best Rate MB/s  Avg time     Min time     Max time
       Triad:          13991.7     0.017174     0.017153     0.017192
    '''

    def __init__(self):
        self.descr = 'STREAM Benchmark'
        self.exclusive_access = True
        self.valid_systems = ['cyclone:cpu']
        self.valid_prog_environs = ['PrgEnv-gnu-nocuda', 'PrgEnv-intel']

        self.use_multithreading = False

        self.prgenv_flags = {
            'PrgEnv-gnu-nocuda': ['-fopenmp', '-O3'],
            'PrgEnv-intel': ['-qopenmp', '-O3'],
        }

        self.exclusive_access = True
        self.sourcepath = 'stream.c'
        self.build_system = 'SingleSource'
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.stream_cpus_per_task = {
            'cyclone:cpu': 20,
        }
        self.env_vars = {
            'OMP_PLACES': 'threads',
            'OMP_PROC_BIND': 'spread'
        }
        self.sanity_patterns = sn.assert_found(
            r'Solution Validates: avg error less than', self.stdout)
        self.perf_patterns = {
            'copy': sn.extractsingle(r'Copy:\s+(?P<triad>\S+)\s+\S+',
                                      self.stdout, 'triad', float),
            'scale': sn.extractsingle(r'Scale:\s+(?P<triad>\S+)\s+\S+',
                                      self.stdout, 'triad', float),
            'add': sn.extractsingle(r'Add:\s+(?P<triad>\S+)\s+\S+',
                                      self.stdout, 'triad', float),
            'triad': sn.extractsingle(r'Triad:\s+(?P<triad>\S+)\s+\S+',
                                      self.stdout, 'triad', float)
        }
        self.stream_bw_reference = {
            'PrgEnv-gnu-nocuda': {
                'cyclone:cpu': {'copy': (90400, -0.05, None, 'MB/s'),
                                'scale': (77100, -0.05, None, 'MB/s'),
                                'add': (77600, -0.05, None, 'MB/s'),
                                'triad': (79300, -0.05, None, 'MB/s')},
            },
            'PrgEnv-intel': {
                'cyclone:cpu': {'copy': (92900, -0.05, None, 'MB/s'),
                                'scale': (91600, -0.05, None, 'MB/s'),
                                'add': (96700, -0.05, None, 'MB/s'),
                                'triad': (96700, -0.05, None, 'MB/s')},
            },
        }
        self.tags = {'production'}
        self.maintainers = ['CS']

    @run_after('setup')
    def prepare_test(self):
        self.num_cpus_per_task = self.stream_cpus_per_task.get(
            self.current_partition.fullname, 1)
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        envname = self.current_environ.name

        self.build_system.cflags = self.prgenv_flags.get(envname, ['-O3'])

        try:
            self.reference = self.stream_bw_reference[envname]
        except KeyError:
            self.reference = self.stream_bw_reference['PrgEnv-gnu-nocuda']