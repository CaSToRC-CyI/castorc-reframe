import reframe as rfm
import reframe.utility.sanity as sn


# Distributed STREAM
#
# Test that runs STREAM in parallel to measure memory performance of many-core
# compute nodes. The code used is a modified version of DitributedStream from
# https://github.com/adrianjhpc/DistributedStream which was originally written
# by Adrian Jackson, EPCC. The modification removed the dependence on the MXML
# library to provide a simpler test program
#


@rfm.simple_test
class StreamTest(rfm.RegressionTest):
    def __init__(self):
        self.valid_systems = ["cyclone:cpu"]
        self.valid_prog_environs = ["PrgEnv-gnu-nocuda"]
        self.build_system = "Make"
        self.executable = "distributed_streams"
        self.use_multithreading = False
        self.sanity_patterns = sn.assert_found(r"Node Triad", self.stdout)
        self.perf_patterns = {
            "Copy": sn.extractsingle(
                r"Node Copy:(\s+\S+:){0}\s+(?P<val>\S+):",
                self.stdout,
                "val",
                float,
                item=-1,
            ),
            "Scale": sn.extractsingle(
                r"Node Scale:(\s+\S+:){0}\s+(?P<val>\S+):",
                self.stdout,
                "val",
                float,
                item=-1,
            ),
            "Add": sn.extractsingle(
                r"Node Add:(\s+\S+:){0}\s+(?P<val>\S+):",
                self.stdout,
                "val",
                float,
                item=-1,
            ),
            "Triad": sn.extractsingle(
                r"Node Triad:(\s+\S+:){0}\s+(?P<val>\S+):",
                self.stdout,
                "val",
                float,
                item=-1,
            ),
        }
        self.reference = {
            "cyclone:cpu": {
                "Copy": (149000, -0.05, 0.05, "MB/s"),
                "Scale": (141700, -0.05, 0.05, "MB/s"),
                "Add": (154500, -0.05, 0.05, "MB/s"),
                "Triad": (156300, -0.05, 0.05, "MB/s"),
            }
        }

        # System specific settings
        self.ntasks = {
            "cyclone:cpu": 240,
        }
        self.ntasks_per_node = {
            "cyclone:cpu": 40,
        }
        # These are the arguments to DistributedStream itself:
        #   arg1: number of elements in each array created. Should exceed the size of
        #         the highest cache level. (Arrays are double precision.)
        #   arg2: the number of repetitions of the benchmark

        self.args = {
            "cyclone:cpu": ["4500000", "1000"],
        }

        self.maintainers = ["cstyl"]
        self.tags = {"benchmark", "diagnostic", "maintenance", "performance"}

    @run_before("run")
    def set_num_threads(self):
        num_tasks = self.ntasks.get(self.current_partition.fullname, 1)
        self.num_tasks = num_tasks
        num_tasks_per_node = self.ntasks_per_node.get(
            self.current_partition.fullname, 1
        )
        self.num_tasks_per_node = num_tasks_per_node
        self.num_cpus_per_task = 1
        self.time_limit = "20m"
        args = self.args.get(self.current_partition.fullname, ["24000000", "10000"])
        self.executable_opts = args
