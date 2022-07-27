"""
Test the average latency of launch a TD vm
"""

import imp
import logging
import pytest

from pycloudstack.vmparam import VM_STATE_SHUTDOWN, VM_STATE_RUNNING, \
    VM_STATE_PAUSE, VM_TYPE_TD, VM_TYPE_EFI, VM_TYPE_LEGACY, VMSpec


__author__ = 'fabing'

LOG = logging.getLogger(__name__)
logging.disable(logging.DEBUG)

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.vm_image("latest-guest-image"),
    pytest.mark.vm_kernel("latest-guest-kernel"),
]


def test_tdvm_lifecycle_virsh(vm_factory):
    """
    Test the basic states

    Step 1: Create and start TD guest
    Step 2: Suspend TD guest and check whether status is paused
    Step 3: Resume TD guest and check whether status is running
    Step 4: Reboot TD guest and check whether status is running
    Step 5: Shutdown TD guest and check whether status is shutdown
    Step 6: Start TD guest and check whether status is running
    """

    cpus = [i for i in range(4, 64, 4)]
    memsize = [i for i in range(4, 128, 8)]
    for cores in cpus:
        for mem in memsize:
            for _ in range(20):
                LOG.info("VM with {} CPU and {} GB vRAM".format(cores, mem))
                vm = VMSpec(sockets=1, cores = cores, threads=1, memsize=mem*1024*1024)

                LOG.info("Create TD guest")
                inst = vm_factory.new_vm(VM_TYPE_TD, auto_start=False, vmspec=vm)
                inst.wait_for_ssh_ready()

                LOG.info("Suspend TD guest")
                inst.suspend()
                ret = inst.wait_for_state(VM_STATE_PAUSE)
                assert ret, "Suspend timeout"

                LOG.info("Resume TD guest")
                inst.resume()
                ret = inst.wait_for_state(VM_STATE_RUNNING)
                assert ret, "Resume timeout"

                LOG.info("Reboot TD guest")
                inst.reboot()
                ret = inst.wait_for_state(VM_STATE_RUNNING)
                assert ret, "Reboot timeout"

                LOG.info("Shutdown TD guest")
                inst.shutdown(mode="acpi")
                ret = inst.wait_for_state(VM_STATE_SHUTDOWN)
                assert ret, "Fail to shutdown instance"

                LOG.info("Start TD guest")
                inst.start()
                ret = inst.wait_for_state(VM_STATE_RUNNING)
                assert ret, "Fail to start instance"

                LOG.info("Destroy TD guest")
                inst.destroy(delete_image=True, delete_log=True)
