import itertools
import os

import reframe as rfm
import reframe.utility.sanity as sn

class GromacsBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        self.valid_prog_environs = ['PrgEnv-gnu-nocuda']
        self.executable = 'gmx_mpi'

        self.keep_files = [output_file]

        energy = sn.extractsingle(r'\s+Potential\s+Kinetic En\.\s+Total Energy'
                                  r'\s+Conserved En\.\s+Temperature\n'
                                  r'(\s+\S+){2}\s+(?P<energy>\S+)(\s+\S+){2}\n'
                                  r'\s+Pressure \(bar\)\s+Constr\. rmsd',
                                  output_file, 'energy', float, item=-1)
        energy_reference = -12071400.0

        self.sanity_patterns = sn.all([
            sn.assert_found('Finished mdrun', output_file),
            sn.assert_reference(energy, energy_reference, -0.01, 0.01)
        ])

        self.perf_patterns = {
            'perf': sn.extractsingle(r'Performance:\s+(?P<perf>\S+)',
                                     output_file, 'perf', float)
        }

        
        self.maintainers = ['CS']
        self.strict_check = False
        self.strict_check = True
        self.use_multithreading = False
        self.num_nodes = 2
        
        self.tags = {'applications','performance'}

@rfm.simple_test
class GromacsCPUCheck(GromacsBaseCheck):

    valid_systems = ['cyclone:cpu']
    # Number of cores for each system
    cores = variable(dict, value={
        'cyclone:cpu': 40,
    })
    exclusive_access = True

    def __init__(self):
        super().__init__('md.log')
        self.descr = 'GROMACS check'
        self.executable_opts = ('mdrun -noconfout -s gmx_1400k_atoms.tpr ').split()
        self.modules = ['GROMACS/2021.5-foss-2021b']
        self.reference = {
                'cyclone:cpu': {'perf': (5.49, -0.01, None, 'ns/day'),
                # 'cyclone:cpu': {'perf': (10.21, -0.01, 0.01, 'ns/day'),
            }
        }

    
    @run_before('run')
    def setup_resources(self):
        self.num_tasks_per_node = self.cores.get(self.current_partition.fullname, 1)
        self.num_tasks = self.num_tasks_per_node * self.num_nodes
        self.num_cpus_per_task = 1
        self.time_limit = '1h'
        self.env_vars = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }