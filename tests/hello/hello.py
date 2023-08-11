import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HelloMultiLangTest(rfm.RegressionTest):
    lang = parameter(["c", "cpp", "f90"])

    valid_systems = ["*"]
    valid_prog_environs = ["*"]

    @run_before("compile")
    def set_sourcepath(self):
        self.sourcepath = f"hello.{self.lang}"

    @sanity_function
    def assert_hello(self):
        return sn.assert_found(r"Hello, World\!", self.stdout)
