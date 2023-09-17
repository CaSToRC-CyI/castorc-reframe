site_configuration = {
    "systems": [
        {
            "name": "cyclone",
            "descr": "Cyclone",
            "hostnames": ["front02"],
            "modules_system": "lmod",  # Lua impl of environment modules
            "partitions": [
                {
                    "name": "login",
                    "descr": "Login nodes",
                    "scheduler": "local",
                    "launcher": "local",
                    "environs": [
                        "PrgEnv-gnu-nompi-nocuda",
                        "PrgEnv-gnu-nocuda",
                        "PrgEnv-nvidia",
                        "PrgEnv-gnu",
                        "PrgEnv-intel-nompi",
                        "PrgEnv-intel",
                    ],
                },
                {
                    "name": "cpu",
                    "descr": "CPU-only nodes (Intel)",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--hint=nomultithread",
                        "--distribution=block:block",
                        "--partition=cpu",
                        "-A p168",
                    ], 
                    "environs": [
                        "PrgEnv-gnu-nompi-nocuda",
                        "PrgEnv-gnu-nocuda",
                        "PrgEnv-intel-nompi",
                        "PrgEnv-intel",
                    ],
                    "max_jobs": 16,
                },
                {
                    "name": "gpu",
                    "descr": "Hybrid nodes (V100/Intel)",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--hint=nomultithread",
                        "--distribution=block:block",
                        "--partition=gpu",
                        "-A p168",
                    ],
                    "environs": [
                        "PrgEnv-gnu-nompi-nocuda",
                        "PrgEnv-gnu-nocuda",
                        "PrgEnv-nvidia",
                        "PrgEnv-gnu",
                        "PrgEnv-intel-nompi",
                        "PrgEnv-intel",
                    ],
                    "max_jobs": 16,
                    "features": ["gpu", "nvgpu"],
                    "resources": [
                        {"name": "gres", "options": ["--gres=gpu:{num_gpus_per_node}"]},
                    ],
                    "devices": [{"type": "gpu", "arch": "sm_70", "num_devices": 4}],
                },
            ],
        }
    ],
    "environments": [
        {
            "name": "PrgEnv-gnu-nompi-nocuda",
            "target_systems": ["cyclone"],
            "modules": ["GCC/12.2.0"],
            "cc": "gcc",
            "cxx": "g++",
            "ftn": "gfortran",
        },
        {
            "name": "PrgEnv-gnu-nocuda",
            "target_systems": ["cyclone"],
            "modules": ["OpenMPI/4.1.4-GCC-12.2.0"],
            "cc": "mpicc",
            "cxx": "mpicxx",
            "ftn": "mpif90",
        },
        {
            "name": "PrgEnv-nvidia",
            "target_systems": ["cyclone"],
            "modules": ["GCC/12.2.0", "CUDA/11.7.0"],
            "cc": "nvcc",
            "cxx": "nvcc",
            "ftn": "gfortran",
        },
        {
            "name": "PrgEnv-gnu",
            "target_systems": ["cyclone"],
            "modules": ["OpenMPI/4.1.4-GCC-12.2.0", "CUDA/11.7.0"],
            "cc": "mpicc",
            "cxx": "mpicxx",
            "ftn": "mpif90",
        },
        {
            "name": "PrgEnv-intel-nompi",
            "target_systems": ["cyclone"],
            "modules": ["intel-compilers/2022.2.1"],
            "cc": "icc",
            "cxx": "icpc",
            "ftn": "ifort",
        },
        {
            "name": "PrgEnv-intel",
            "target_systems": ["cyclone"],
            "modules": ["intel/2022b"],
            "cc": "mpiicc",
            "cxx": "mpiicpc",
            "ftn": "mpiifort",
        },
    ],  # end of environments
    "logging": [
        {
            "level": "debug",
            "handlers": [
                {
                    "type": "stream",
                    "name": "stdout",
                    "level": "info",
                    "format": "%(message)s",
                },
                {
                    "type": "file",
                    "level": "debug",
                    "format": "[%(asctime)s] %(levelname)s: %(check_info)s: %(message)s",  # noqa: E501
                    "append": False,
                },
            ],
            "handlers_perflog": [
                {
                    "type": "filelog",
                    "prefix": "%(check_system)s/%(check_partition)s",
                    "level": "info",
                    "format": (
                        "%(check_job_completion_time)s|reframe %(version)s|"
                        "%(check_info)s|jobid=%(check_jobid)s|"
                        "%(check_perf_var)s=%(check_perf_value)s|"
                        "ref=%(check_perf_ref)s "
                        "(l=%(check_perf_lower_thres)s, "
                        "u=%(check_perf_upper_thres)s)|"
                        "%(check_perf_unit)s"
                    ),
                    "append": True,
                }
            ],
        }
    ],
    # rfmdocend: logging
}
