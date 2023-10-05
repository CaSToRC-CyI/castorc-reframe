import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class pytorch_distr_cnn(rfm.RunOnlyRegressionTest):
    descr = 'Check the training throughput of a cnn with torch.distributed'
    valid_systems = ['cyclone:gpu']
    valid_prog_environs = ['PrgEnv-gnu']
    sourcesdir = 'src'
    exclusive_access = True
    use_multithreading = False
    num_tasks = 16
    num_tasks_per_node = 4
    num_nodes = num_tasks // num_tasks_per_node
    num_gpus_per_node = num_tasks_per_node
    throughput_per_gpu = 309.61
    executable = 'python cnn_distr.py'
    throughput_total = throughput_per_gpu * num_tasks

    reference = {
        "cyclone:gpu": {
            "samples_per_sec_per_gpu": (throughput_per_gpu, -0.1, None, "samples/sec"),
            "samples_per_sec_total": (throughput_total, -0.1, None, "samples/sec"),
        }
    }

    tags = {'production'}
    modules = ['torchvision/0.13.1-foss-2022a-CUDA-11.7.0']

    @sanity_function
    def assert_job_is_complete(self):
        return sn.assert_found(r"Total average", self.stdout)

    @performance_function("samples/sec")
    def samples_per_sec_per_gpu(self):
        return sn.avg(
            sn.extractall(
                r"Epoch\s+\d+\:\s+(?P<samples_per_sec_per_gpu>\S+)\s+images",
                self.stdout,
                "samples_per_sec_per_gpu",
                float,
            )
        )

    @performance_function("samples/sec")
    def samples_per_sec_total(self):
        return sn.avg(
            sn.extractall(
                r"Total average: (?P<samples_per_sec_total>\S+)\s+images",
                self.stdout,
                "samples_per_sec_total",
                float,
            )
        )

    @run_before("run")
    def set_visible_devices_per_rank(self):
        self.job.launcher.options.append("./set_visible_devices.sh")

    @run_before("run")
    def set_job_options(self):
        self.job.options = [
            f"--nodes={self.num_nodes}",
            f"--gres=gpu:{self.num_gpus_per_node}",
        ]
