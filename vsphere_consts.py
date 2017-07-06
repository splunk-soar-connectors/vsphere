# --
# File: vsphere_consts.py
#
# Copyright (c) Phantom Cyber Corporation, 2014-2017
#
# This unpublished material is proprietary to Phantom Cyber.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Phantom Cyber.
#
# --

# Json keys specific to vsphere app's input parameters/config and the output result
VSPHERE_JSON_VMX_PATH = "vmx_path"
VSPHERE_JSON_TOTAL_GUESTS = "total_vms"
VSPHERE_JSON_TOTAL_GUESTS_RUNNING = "running_vms"
VSPHERE_JSON_GUEST_NAME = "vm_name"
VSPHERE_JSON_GUEST_FULL_NAME = "vm_full_name"
VSPHERE_JSON_DISPLAY_NAME = 'display_name'
VSPHERE_JSON_GUEST_HOST_NAME = "vm_hostname"
VSPHERE_JSON_SNAP_NAME = "snapshot"
VSPHERE_JSON_IP_HOSTNAME = "ip_hostname"

# Status messages for vsphere app
VSPHERE_ERR_SERVER_CONNECT = "Connection to {server_ip} failed"
VSPHERE_SUCC_CANT_EXEC = "Cannot execute {action} since current state of vm is {state}"
VSPHERE_ERR_CANNOT_FIND_SNAPSHOT_LIST_FILE = "Cannot find snapshot list file"
VSPHERE_ERR_SNAPSHOT_PATH = "Cannot find path for snapshot '{}'"
VSPHERE_ERR_CANNOT_GET_CONTENT_LENGTH = "Unable to detect the content length of the file"
VSPHERE_ERR_CANNOT_FIND_SUSPEND_FILE = "Unable to locate suspend file"
VSPHERE_ERR_SNAPSHOT_URL = "Could not create url to file for snapshot '{}'"
VSPHERE_ERR_VM_FROM_VMX_PATH = "Could not get vm object from the vmx path"
VSPHERE_ERR_CANNOT_MAKE_TEMP_FOLDER = "Cannot make temp folder"
VSPHERE_SUCC_CONNECTIVITY_TEST = "Connectivity test passed"
VSPHERE_ERR_CONNECTIVITY_TEST = "Connectivity test failed"
VSPHERE_ERR_FAILED_TO_GET_SNAPSHOT_INFO = "Failed to get information of latest snapshot"
VSPHERE_ERR_SERVER_CONNECTION = "Server connection error"
VSPHERE_ERR_SERVER_RETURNED_STATUS_CODE = "Server returned error code: {code}"

# Progress messages format string
VSPHERE_PROG_SUSPEND_FILE_DOWNLOADING = "Downloading suspend file"
VSPHERE_PROG_SUSPENDED = "Guest suspended"
VSPHERE_PROG_SNAPSHOT_REVERTED = "Reverted to snapshot"
VSPHERE_PROG_SKIPPING_SUSPEND = "Skipping guest suspension due to state being {state}"
VSPHERE_PROG_SNAPSHOT_NAME = "Creating snapshot named '{snap_name}'"
VSPHERE_PROG_SNAPSHOT_TAKEN = "Created snapshot"
VSPHERE_PROG_TASK_QUEUED = "Task queued"
VSPHERE_PROG_TASK_COMPLETED_PERCENT = "Task '{task_name}' {progress}% completed"
VSPHERE_PROG_TASK_RUNNING = "Task running"
VSPHERE_PROG_SNAPSHOT_DOWNLOADING = "Downloading snapshot file for '{snap_name}'"
VSPHERE_PROG_SNAPSHOT_INFO_DOWNLOADING = "Downloading snapshot information file for '{snap_name}'"
VSPHERE_PROG_FINISHED_DOWNLOADING_STATUS = "Finished downloading {0:.0%}"

# Other constants used in the connector
VSPHERE_CONST_VM_STATE_RUNNING = "running"
VSPHERE_CONST_VM_STATE_NOT_RUNNING = "not_running"
VSPHERE_CONST_SNAPSHOT_NAME_PREFIX = "PH_Snapshot_"
VSPHERE_CONST_SNAPSHOT_DESCRIPTION = "Snapshot taken by Phantom for container {container_id}"
VSPHERE_CONST_SNAPSHOT_FILE_TYPE = "vm snapshot file"
VSPHERE_CONST_SUSPEND_FILE_TYPE = "vm suspend file"
VSPHERE_CONST_DEFAULT_DATACENTER = "ha-datacenter"
VSPHERE_CONST_URL = "url"
VSPHERE_CONST_DATACENTER = "dcPath"
VSPHERE_CONST_DATASTORE = "dsName"

# This text is compared with an error that we get from the vsphere server, don't change
# If you need to change this, then change this value to a list and add the newer string to it.
# In the code compare it with the list
VSPHERE_VIRTUAL_MACHINE_NOT_CHANGED = "Snapshot not taken since the state of the virtual machine has not changed since the last snapshot operation"
