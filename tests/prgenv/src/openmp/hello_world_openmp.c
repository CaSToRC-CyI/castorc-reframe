#include <omp.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
  int tid, nthreads;

#pragma omp parallel private(tid, nthreads)
  {
    tid      = omp_get_thread_num();
    nthreads = omp_get_num_threads();
    printf("Hello, World from thread %d out of %d from process %d out of %d\n",
           tid, nthreads, 0, 1);
  }
  return EXIT_SUCCESS;
}
