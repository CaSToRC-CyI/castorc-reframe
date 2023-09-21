#!/bin/sh
set -e
staged_dir=$(pwd)
mkdir -p ${WRITE_DIR}
cd ${WRITE_DIR}

# mkdir -p  striped
mkdir -p unstriped
# mkdir -p fullstriped

# #lfs setstripe -c 1 unstriped
# beegfs-ctl --mount=/nvme/h/ --setpattern --numtargets=1 unstriped
# #lfs setstripe -c -1 fullstriped
# beegfs-ctl --mount=/nvme/h/ --setpattern --numtargets=-1 fullstriped
# #lfs setstripe -c 4 striped
# beegfs-ctl --mount=/nvme/h/ --setpattern --numtargets=4 striped