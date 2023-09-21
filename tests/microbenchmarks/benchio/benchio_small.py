# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
import os 
import contextlib

@rfm.simple_test
class benchioSmallTest(rfm.RegressionTest):

    valid_systems = ['cyclone:cpu']
    valid_prog_environs = ['PrgEnv-gnu-nocuda']

    tags = {'performance','short','io'}
    num_nodes = parameter([1,2])

    benchmark_info = parameter([
        ('nvme', '/nvme/h/cy21cs1/reframe_data'),
        ('scratch', '/nvme/scratch/cy21cs1/reframe_data'),
    ], fmt=lambda x: x[0], loggable=True)

    exclusive_access = True

    # Number of cores for each system
    cores = variable(dict, value={
        'cyclone:cpu': 40,
    })

    allref = {
        'nvme': {
            1: {
                'cyclone:cpu': {
                    'unstriped_mpiio': (1.1, -0.8, 0.8 ,'GB/s')
                }
            },
            2: {
                'cyclone:cpu': {
                    'unstriped_mpiio': (1.6, -0.8, 0.8 ,'GB/s')
                },
            }
        },
        'scratch': {
            1: {
                'cyclone:cpu': {
                    'unstriped_mpiio': (1.4, -0.8, 0.8 ,'GB/s')
                },
            },
            2: {
                'cyclone:cpu': {
                    'unstriped_mpiio': (2.5, -0.8, 0.8 ,'GB/s')
                },
            }
        }
    }

    def __init__(self,**kwds):

        super().__init__()
        self.executable_opts = ('1260 1260 1260 global mpiio unstriped').split()
        self.env_vars = {
            "OMP_NUM_THREADS": '1',
            'I_MPI_PMI_LIBRARY': '/usr/lib64/libpmi.so',
        }

        self.prerun_cmds  = ['source create_striped_dirs.sh']
        self.postrun_cmds  = ['source delete_dirs.sh']
        self.time_limit = '9m'
        self.build_system = 'CMake'
        self.modules = ["CMake/3.24.3-GCCcore-12.2.0"]
        self.perf_patterns = {
            'unstriped_mpiio': sn.extractsingle(r'Writing to unstriped/mpiio\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)',
                                    self.stdout, 1, float),
        }

        if self.num_nodes not in [1, 2]:
            raise Exception("References are defined for calculations with 8 nodes")


    @run_after('init')
    def setup_ref_by_storage(self):
        with contextlib.suppress(KeyError):
            self.reference = self.allref[self.benchmark_info[0]][self.num_nodes]


    @run_before('run')
    def setup_run(self):
        stagedir_name=os.path.split( self.stagedir )[-1]
        self.env_vars["WRITE_DIR"]=os.path.join(self.benchmark_info[1],stagedir_name)
        self.executable= self.stagedir + "/src/benchio"


    @run_before('run')
    def setup_resources(self):
        self.num_tasks_per_node = self.cores.get(self.current_partition.fullname, 1)
        self.num_tasks = self.num_tasks_per_node * self.num_nodes
        self.num_cpus_per_task = 1
    

    @sanity_function
    def assert_benchio(self):
        return sn.assert_found(r'Finished', self.stdout)