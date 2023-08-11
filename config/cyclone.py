site_configuration = {
    'systems': [
        {
            'name': 'cyclone',
            'descr': 'Cyclone',
            'hostnames': ['front02'],
            'modules_system': 'lmod', # Lua impl of environment modules
            'partitions': [
                {
                    'name': 'login',
                    'descr': 'Login nodes',
                    'scheduler': 'local',
                    'launcher': 'local',
                    # 'environs': ['builtin', 'gnu', 'intel', 'nvidia'],
                    'environs': ['builtin', 'gnu', 'intel'],
                },
                {
                    'name': 'cpu',
                    'descr': 'CPU-only nodes (Intel)',
                    'scheduler': 'slurm',
                    'launcher': 'srun',
                    'access': ['--hint=nomultithread','--distribution=block:block','--partition=cpu', '-A p163'], # TODO: Change to it's own project
                    'environs': ['gnu', 'intel'],
                    'max_jobs': 16,
                },
                # {
                #     'name': 'gpu',
                #     'descr': 'Hybrid nodes (V100/Intel)',
                #     'scheduler': 'slurm',
                #     'launcher': 'srun',
                #     'access': ['--hint=nomultithread','--distribution=block:block','--partition=gpu', '-A p163'], # TODO: Change to it's own project
                #     'environs': ['gnu', 'intel', 'nvidia'],
                #     'max_jobs': 16,
                # }
            ]
        }
    ],
    'environments': [
        {
            'name': 'gnu',
            # 'modules': ['GCC/11.3.0'],
            'modules': ['OpenMPI/4.1.1-GCC-11.2.0'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
            'target_systems': ['cyclone']
        },
        {
            'name': 'intel',
            # 'modules': ['intel-compilers/2022.2.1'],
            'modules': ['impi/2021.7.1-intel-compilers-2022.2.1'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort',
            'target_systems': ['cyclone']
        },
        # {
        #     'name': 'nvidia',
        #     'modules': ['CUDA/11.7.0'],
        #     'cc': 'nvcc',
        #     'cxx': 'nvcc',
        #     'ftn': '',
        #     'target_systems': ['cyclone']
        # },
        {
            'name': 'builtin',
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': '',
            'target_systems': ['cyclone']
        }
    ],  # end of environments
    'logging': [
        {
            'level': 'debug',
            'handlers': [
                {
                    'type': 'stream',
                    'name': 'stdout',
                    'level': 'info',
                    'format': '%(message)s'
                },
                {
                    'type': 'file',
                    'level': 'debug',
                    'format': '[%(asctime)s] %(levelname)s: %(check_info)s: %(message)s',   # noqa: E501
                    'append': False
                }
            ],
            'handlers_perflog': [
                {
                    'type': 'filelog',
                    'prefix': '%(check_system)s/%(check_partition)s',
                    'level': 'info',
                    'format': (
                        '%(check_job_completion_time)s|reframe %(version)s|'
                        '%(check_info)s|jobid=%(check_jobid)s|'
                        '%(check_perf_var)s=%(check_perf_value)s|'
                        'ref=%(check_perf_ref)s '
                        '(l=%(check_perf_lower_thres)s, '
                        'u=%(check_perf_upper_thres)s)|'
                        '%(check_perf_unit)s'
                    ),
                    'append': True
                }
            ]
        }
    ],
    # rfmdocend: logging
}