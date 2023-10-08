# CaSToRC ReFrame Tests
Repository for Reframe Configuration and Tests for Cyclone.

## Structure
- `config/`: configuration files for the different partitions of Cyclone.
- `tests/`: test library. All tests should be configured so that they run on all available partitions, wherever possible.
    - `apps/`: Benchmarks to evaluate the performance of specific applications such as GROMACS, pyTorch etc.
    - `microbenchmarks/`: Small benchmarks that measure compute, memory, IO and communication performance to evaluate the performance of the system.
    - `prgenv/`: Tests that ensure the system can compile and run code across the available compilers in C, C++ and Fortran.

## Executing the test suite.
To run the tests first the `ReFrame` library has to be loaded:
```sh
$ module load ReFrame
```

### Run all tests
To list all the available tests:
```sh
$ reframe -C config/cyclone.py -c tests -R -l
```

This will output a list of all the available tests that will be executed. To actually run the tests, run the following command:
```sh
$ reframe -C config/cyclone.py -c tests -R -r
```

### Run specific tests
Alternatively, you may only wish to run a subset of tests. To run a specific test
```sh
$ reframe -C config/cyclone.py -c *path-to-a-test* -r
```

To run all tests in a directory:
```sh
$ reframe -C config/cyclone.py -c *path-to-a-test-directory* -R -r
```

### Run tests in a group
Tests are also organized in the following categories:
- `benchmark`: Identifies microbenchmarks.
- `diagnostic`: Identifies benchmarks that diagnose the state of the system.
- `maintenance`: Identifies benchmarks that should run after the end of a maintenance session.
- `applications`: Identifies application benchmarks.
- `performance`: Identifies benchmarks that give us a picture of the performance capabilities of the system.

To run all tests in a category:
```sh
$ reframe -C config/cyclone.py -c tests --tag=<category> -R -r
```