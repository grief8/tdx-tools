"""
Test the average latency of launch a TD vm
"""

import imp
import logging
import pytest

from pycloudstack.vmparam import VM_STATE_SHUTDOWN, VM_STATE_RUNNING, \
    VM_STATE_PAUSE, VM_TYPE_TD, VM_TYPE_LEGACY, VMSpec


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

    LOG.info("Create TD guest")
    inst = vm_factory.new_vm(VM_TYPE_TD, auto_start=True, vmspec=VMSpec.model_base())
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
    inst.shutdown()
    ret = inst.wait_for_state(VM_STATE_SHUTDOWN)
    assert ret, "Fail to shutdown instance"

    LOG.info("Start TD guest")
    inst.start()
    ret = inst.wait_for_state(VM_STATE_RUNNING)
    assert ret, "Fail to start instance"
