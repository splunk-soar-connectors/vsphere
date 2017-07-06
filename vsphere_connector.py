# --
# File: vsphere_connector.py
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


# Phantom imports
import phantom.app as phantom

from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

from phantom.vault import Vault

# THIS Connector imports
from vsphere_consts import *

import os
import re
import ssl
from collections import defaultdict
from pysphere import VIServer
import time
from time import mktime
import requests
from requests.auth import HTTPBasicAuth
from tempfile import mkdtemp

requests.packages.urllib3.disable_warnings()  # pylint: disable=E1101


class VsphereConnector(BaseConnector):

    # Actions supported by this script
    ACTION_ID_GET_REGISTERED_GUESTS = "list_vms"
    ACTION_ID_GET_RUNNING_GUESTS = "get_running_guests"
    ACTION_ID_START_GUEST = "start_guest"
    ACTION_ID_STOP_GUEST = "stop_guest"
    ACTION_ID_SUSPEND_GUEST = "suspend_guest"
    ACTION_ID_TAKE_SNAPSHOT = "take_snapshot"
    ACTION_ID_REVERT_VM = "revert_vm"
    ACTION_ID_GET_SYSTEM_INFO = "get_system_info"

    def __init__(self):

        # Call the BaseConnectors init first
        super(VsphereConnector, self).__init__()

        self._vs_server = None
        self._datacenters = list()
        self._verify = False

        # Connector result global object
        self._vs_server = VIServer()

    def initialize(self):

        config = self.get_config()

        self._verify = config.get('verify_server_cert', False)

        # setup the auth
        self._auth = HTTPBasicAuth(config[phantom.APP_JSON_USERNAME], config[phantom.APP_JSON_PASSWORD])

        self.debug_print('self.status', self.get_status())

        return phantom.APP_SUCCESS

    def _connect_to_server(self, config):
        """Function that logins to the vsphere server

            Args:
                config: The json object containing config

            Return:
                A status code
        """

        if (self._vs_server.is_connected()):
            return phantom.APP_SUCCESS

        if (self._verify is False):
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass

        server = config[phantom.APP_JSON_SERVER]
        username = config[phantom.APP_JSON_USERNAME]
        password = config[phantom.APP_JSON_PASSWORD]

        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, server)

        try:
            self._vs_server.connect(server, username, password)
        except Exception as e:
            return self.set_status_save_progress(phantom.APP_ERROR, VSPHERE_ERR_SERVER_CONNECT, e, server_ip=server)

        # Get the datacenters
        datacenters = self._vs_server.get_datacenters()

        self._datacenters = [v for k, v in datacenters.items()]

        return phantom.APP_SUCCESS

    def _get_system_info(self, config, param):

        # Connect to the server
        status_code = self._connect_to_server(config)

        if (phantom.is_fail(status_code)):
            return status_code

        # Add the action result
        action_result = self.add_action_result(ActionResult(dict(param)))

        total_vms = 0
        matched = False

        ip_hostname = param[VSPHERE_JSON_IP_HOSTNAME]

        for datacenter in self._datacenters:

            vm_list = self._vs_server.get_registered_vms(datacenter=datacenter)

            total_vms += len(vm_list)

            for curr_vmx_path in vm_list:

                # get the vm object
                vm = self._vs_server.get_vm_by_path(curr_vmx_path, datacenter)

                ip = vm.get_property('ip_address')
                hostname = vm.get_property('hostname')

                if ((ip_hostname != ip) and (ip_hostname != hostname)):
                    continue

                # one of the params matched
                curr_data = action_result.add_data({})
                curr_data[VSPHERE_JSON_VMX_PATH] = "[{0}]".format(datacenter) + curr_vmx_path
                curr_data[phantom.APP_JSON_IP] = ip
                curr_data[VSPHERE_JSON_GUEST_NAME] = vm.get_property('name')
                curr_data[VSPHERE_JSON_GUEST_HOST_NAME] = hostname
                curr_data[VSPHERE_JSON_GUEST_FULL_NAME] = vm.get_property('guest_full_name')

                if (vm.is_powered_on()):
                    curr_data[phantom.APP_JSON_STATE] = VSPHERE_CONST_VM_STATE_RUNNING
                else:
                    curr_data[phantom.APP_JSON_STATE] = VSPHERE_CONST_VM_STATE_NOT_RUNNING

                # Found the endpoint, so break
                matched = True
                break

        # update the summary value about the total guests
        action_result.update_summary({'total_vms_searched': total_vms})
        action_result.update_summary({'found_endpoint': matched})

        action_result.set_status(phantom.APP_SUCCESS)

    def _get_vms(self, action, config, param):
        """Function that handles ACTION_ID_GET_REGISTERED_GUESTS and
           ACTION_ID_GET_RUNNING_GUESTS

            Args:

            Return:
                A status code
        """

        # Connect to the server
        status_code = self._connect_to_server(config)

        if (phantom.is_fail(status_code)):
            return status_code

        # Add the action result
        action_result = self.add_action_result(ActionResult(dict(param)))

        total_vms = 0
        total_running = 0

        for datacenter in self._datacenters:

            if (action == self.ACTION_ID_GET_RUNNING_GUESTS):
                vm_list = self._vs_server.get_registered_vms(status='poweredOn', datacenter=datacenter)
            else:
                vm_list = self._vs_server.get_registered_vms(datacenter=datacenter)

            total_vms += len(vm_list)

            for curr_vmx_path in vm_list:

                # get the vm object
                vm = self._vs_server.get_vm_by_path(curr_vmx_path, datacenter)
                curr_data = action_result.add_data({})
                curr_data[VSPHERE_JSON_VMX_PATH] = "[{0}]".format(datacenter) + curr_vmx_path
                curr_data[phantom.APP_JSON_IP] = vm.get_property('ip_address')
                curr_data[VSPHERE_JSON_GUEST_NAME] = vm.get_property('name')
                curr_data[VSPHERE_JSON_GUEST_HOST_NAME] = vm.get_property('hostname')
                curr_data[VSPHERE_JSON_GUEST_FULL_NAME] = vm.get_property('guest_full_name')

                if (vm.is_powered_on()):
                    curr_data[phantom.APP_JSON_STATE] = VSPHERE_CONST_VM_STATE_RUNNING
                    total_running += 1
                else:
                    curr_data[phantom.APP_JSON_STATE] = VSPHERE_CONST_VM_STATE_NOT_RUNNING

        # update the summary value about the total guests
        action_result.update_summary({VSPHERE_JSON_TOTAL_GUESTS: total_vms})
        action_result.update_summary({VSPHERE_JSON_TOTAL_GUESTS_RUNNING: total_running})

        action_result.set_status(phantom.APP_SUCCESS)

    def _wait_for_async_task(self, task, action, action_result):
        """Function that asynchronously manages the task object

            Args:
                task: The task object to monitor.
                action: The action that is currently being carried out.
                action_result: The ActionResult object to hold the status

            Return:
                A status code of the type phantom.APP_[SUCC|ERR]_XXX.
        """

        displayed_once = False
        task_name = action.replace('_', ' ')

        while True:

            # interested in all states
            status = task.wait_for_state(['success', 'error', 'queued', 'running'])

            if (status == 'error'):
                action_result.set_status(phantom.APP_ERROR, phantom.APP_ERR_CMD_EXEC)
                action_result.append_to_message(task.get_error_message())
                break
            elif(status == 'success'):
                action_result.set_status(phantom.APP_SUCCESS, phantom.APP_SUCC_CMD_EXEC)
                break
            elif(status == 'queued'):
                self.send_progress(VSPHERE_PROG_TASK_QUEUED)
            elif(status == 'running'):
                progress = task.get_progress()
                if (progress):
                    self.send_progress(VSPHERE_PROG_TASK_COMPLETED_PERCENT,
                            task_name=task_name,
                            progress=progress)
                elif (not displayed_once):
                    self.send_progress(VSPHERE_PROG_TASK_RUNNING)
                    displayed_once = True

            time.sleep(2)

        return action_result.get_status()

    def _parse_vm_path(self, full_vmx_path):

        # The full_vmx_path will be of the format
        # [datacenter_name][datastore_name] <vm_folder>.<vmname>.vmx
        # for e.g. [Datacenter][DAS_labesxi1_1] OpenVAS/OpenVAS.vmx

        search = re.search("\[(.*)\](\[.*)", full_vmx_path)
        if (not search):
            return VSPHERE_CONST_DEFAULT_DATACENTER, full_vmx_path

        datacenter = search.group(1)
        vmx_path = search.group(2)

        return datacenter, vmx_path

    def _handle_start_stop_guest(self, action, config, param):
        """Function that handles ACTION_ID_STOP_GUEST and ACTION_ID_START_GUEST action

            Args:

            Return:
                A status code
        """

        # Connect to the server
        status_code = self._connect_to_server(config)

        if (phantom.is_fail(status_code)):
            return status_code

        # create an action_result
        action_result = self.add_action_result(ActionResult(dict(param)))

        # get the config
        # The path will contain the datacenter also
        datacenter, vmx_path = self._parse_vm_path(param[VSPHERE_JSON_VMX_PATH])

        # Get the vm from the path
        try:
            vm = self._vs_server.get_vm_by_path(vmx_path, datacenter)
        except Exception as e:
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_VM_FROM_VMX_PATH, e)

        task = None
        # Only stop if powered on, else the API returns back an error
        if ((action == self.ACTION_ID_STOP_GUEST) and vm.is_powered_on()):
            task = vm.power_off(sync_run=False)
        # Only start if it can be, else the API returns back an error
        elif ((action == self.ACTION_ID_START_GUEST) and (not vm.is_powered_on())):
            task = vm.power_on(sync_run=False)

        if (task):
            status_code = self._wait_for_async_task(task, action, action_result)
        else:
            # Most probably we don't have to change the state right now, treat this
            # as a success case (debatable)
            action_result.set_status(phantom.APP_SUCCESS, VSPHERE_SUCC_CANT_EXEC,
                    action=action, state=vm.get_status())

        return action_result.get_status()

    def _create_url_from_path(self, server, vm_file_path, datacenter):
        """Function that creates a url from the path

            Args:
            server: The ip or machine name of the esx host
            vm_file_path: The path of the file, it is expected to be of the format
                [<datastore_name>] <folder>/<name>-<random_chars>.<extension>
            datacenter: The text that tell which datacenter to use while creating the url

            Return:
            The url of the file on success.
        """

        # it's always in the following format
        # [datastore1] WXP3x86/WXP3x86-<random_chars>.<extension>

        # print "Got vm_file_path: {}".format(vm_file_path)
        # extract the dsName part
        start = vm_file_path.find('[') + 1
        end = vm_file_path.find(']')
        ds_name = vm_file_path[start:end]
        # print "dsName: '%s'" % ds_name

        # Get the file path after the datastore
        start = vm_file_path.find(']') + 2

        file_path = vm_file_path[start:]

        # now create the query url, which is of the fomat 'https://{}/folder/{}?dcPath={}&dsName={}'

        file_url = {}
        file_url[VSPHERE_CONST_URL] = 'https://{0}/folder/{1}'.format(server, file_path)
        file_url[VSPHERE_CONST_DATACENTER] = datacenter
        file_url[VSPHERE_CONST_DATASTORE] = ds_name

        return file_url

    def _create_url_of_file(self, server, file_type, vm, datacenter, file_name=None):
        """Function that creates a url of a given file that is present on the vm.

            Args:
                server: The ip or machine name of the esx host
                file_type: The file type that must match the type returned using the 'files' property of the vm.
                file_name: The file name that must match the name returned using the 'files' property of the vm.

            Return:
                The url of the file on success, None otherwise.
        """

        # get the files for this vm
        files = vm.get_property('files', from_cache=False)
        # self.debug_print("files data", files)
        vm_file = None

        for k, v in files.items():

            # first match file type
            if (v['type'] != file_type):
                continue

            # file type matched
            if (not file_name):
                # no need to match the name, since type matched, file is found
                vm_file = v['name']
                break

            if ((file_name) and (v['name'].find(file_name) != -1)):
                # file_name is specified and it matched
                vm_file = v['name']
                break

        if (vm_file is None):
            # Not found
            return None

        return self._create_url_from_path(server, vm_file, datacenter)

    def _move_file_to_vault(self, host, container_id, file_size, type_str, local_file_path, result, info, contains):
        """Function that creates a url from the path

            Args:
                host: The ip or machine name of the esx host
                container_id: The container_id to add the file to
                vmx_path: The vmx_path of the vm
                file_size: Size of the file in bytes that is to be added to vault
                type_str: A string representing the type of the file
                local_file_path: The local file path that is to be added to the vault
                result: The ActionResult object to hold the status

            Return:
                A status code of the type phantom.APP_[SUCC|ERR]_XXX
        """

        self.save_progress(phantom.APP_PROG_ADDING_TO_VAULT)

        # lets move the data into the vault
        vault_attach_dict = {}
        vault_attach_dict[phantom.APP_JSON_HOST] = host
        vault_attach_dict[phantom.APP_JSON_INFO] = info
        vault_attach_dict[phantom.APP_JSON_CONTAINS] = contains
        vault_attach_dict[phantom.APP_JSON_SIZE] = file_size
        vault_attach_dict[phantom.APP_JSON_TYPE] = type_str
        vault_attach_dict[phantom.APP_JSON_ACTION_NAME] = self.get_action_name()
        vault_attach_dict[phantom.APP_JSON_APP_RUN_ID] = self.get_app_run_id()

        curr_data = vault_attach_dict

        file_name = os.path.basename(local_file_path)

        try:
            os.chmod(os.path.dirname(local_file_path), 0770)
            vault_ret_dict = Vault.add_attachment(local_file_path, container_id,
                                                    file_name, vault_attach_dict)

        except Exception as e:
            return result.set_status(phantom.APP_ERROR, phantom.APP_ERR_FILE_ADD_TO_VAULT, e)

        if vault_ret_dict.get('succeeded'):
            curr_data[phantom.APP_JSON_VAULT_ID] = vault_ret_dict[phantom.APP_JSON_HASH]
            curr_data[phantom.APP_JSON_NAME] = file_name
            result.add_data(curr_data)
            wanted_keys = [phantom.APP_JSON_VAULT_ID, phantom.APP_JSON_NAME, phantom.APP_JSON_SIZE]
            summary = dict([ (x, curr_data[x]) for x in wanted_keys if x in curr_data ])
            result.update_summary(summary)
            result.set_status(phantom.APP_SUCCESS)
        else:
            result.set_status(phantom.APP_ERROR, phantom.APP_ERR_FILE_ADD_TO_VAULT)
            result.append_to_message(vault_ret_dict['message'])

        return result.get_status()

    def _download_file(self, url_to_download, action_result, local_file_path):
        """Function that downloads the file from a url

            Args:
                url_to_download: the url of the file to download
                action_result: The ActionResult object to hold the status
                local_file_path: The local file path that was created.

            Return:
                A status code of the type phantom.APP_[SUCC|ERR]_XXX.
                The size in bytes of the file downloaded.
        """

        content_size = 0

        # Which percent chunks will the download happen for big files
        percent_block = 10

        # size that sets a file as big.
        # A big file will be downloaded in chunks of percent_block else it will be a synchronous download
        big_file_size_bytes = 20 * (1024 * 1024)

        self.save_progress(phantom.APP_PROG_DOWNLOADING_FILE_FROM_TO,
                src=url_to_download[VSPHERE_CONST_URL], dest=local_file_path)

        self.debug_print("Complete URL", url_to_download)

        # Create the param dictionary
        keys = [VSPHERE_CONST_DATACENTER, VSPHERE_CONST_DATASTORE]
        params = {x: url_to_download[x] for x in keys}

        try:
            r = requests.get(url_to_download[VSPHERE_CONST_URL], params=params, verify=self._verify, auth=self._auth, stream=True)
        except Exception as e:
            return (action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_SERVER_CONNECTION, e), content_size)

        if (r.status_code != requests.codes.ok):  # pylint: disable=E1101
            return (action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_SERVER_RETURNED_STATUS_CODE, code=r.status_code), content_size)

        # get the content length
        content_size = r.headers['content-length']

        if (not content_size):
            return (action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_CANNOT_GET_CONTENT_LENGTH), content_size)

        self.save_progress(phantom.APP_PROG_FILE_SIZE, value=content_size, type='bytes')

        bytes_to_download = int(content_size)

        # init to download the whole file in a single read
        block_size = bytes_to_download

        # if the file is big then download in % increments
        if (bytes_to_download > big_file_size_bytes):
            block_size = (bytes_to_download * percent_block) / 100

        bytes_downloaded = 0

        try:
            with open(local_file_path, 'wb') as file_handle:
                for chunk in r.iter_content(chunk_size=block_size):
                    if (chunk):
                        bytes_downloaded += len(chunk)
                        file_handle.write(chunk)
                        file_handle.flush()
                        os.fsync(file_handle.fileno())
                        self.send_progress(VSPHERE_PROG_FINISHED_DOWNLOADING_STATUS, float(bytes_downloaded) / float(bytes_to_download))
        except Exception as e:
            return (action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_SERVER_CONNECTION, e), content_size)

        return (action_result.set_status(phantom.APP_SUCCESS, phantom.APP_SUCC_FILE_DOWNLOAD), content_size)

    def _parse_snap_list_file(self, local_file_path, snap_name, id):
        """Function that parses the snapshot list file from a local location and return the file name

            Args:

            Return:
                The file name that for the snapshot with 'snap_name' or None if not found

        """

        snap_path = None
        snap_list_dict = defaultdict(dict)
        with open(local_file_path) as f:
            for line in f:
                # extract the snapshot index and values that we are interested in
                # file name
                m = re.search('snapshot([0-9]+)\.filename[ ]*=[ ]*"(.*)"', line)
                if m:
                    index = m.group(1)
                    file_name = m.group(2)
                    # print "File Name: {} at Index: {}".format(file_name, index)
                    snap_list_dict[index].update({'key': index, 'file_name': file_name})
                    # try to see if this is the snapshot we are looking for
                    # see if the display_Name for this snapshot has been filled in
                    if ((VSPHERE_JSON_DISPLAY_NAME) in snap_list_dict[index]):
                        if (snap_list_dict[index][VSPHERE_JSON_DISPLAY_NAME] == snap_name):
                            if (id is None):
                                snap_path = snap_list_dict[index]['file_name']
                                break
                            elif ('id' in snap_list_dict[index]):
                                if (snap_list_dict[index]['id'] == id):
                                    snap_path = snap_list_dict[index]['file_name']
                                    break
                    continue

                # display name
                m = re.search('snapshot([0-9]+)\.displayName[ ]*=[ ]*"(.*)"', line)
                if m:
                    index = m.group(1)
                    display_name = m.group(2)
                    # print "Display Name: {} at Index: {}".format(display_name, index)
                    snap_list_dict[index].update({'key': index, VSPHERE_JSON_DISPLAY_NAME: display_name})

                    # try to see if this is the snapshot we are looking for
                    if (display_name == snap_name):
                        # see if the file name for this snapshot has been filled in
                        if (('file_name') in snap_list_dict[index]):
                            if (id is None):
                                snap_path = snap_list_dict[index]['file_name']
                                break
                            elif ('id' in snap_list_dict[index]):
                                if (snap_list_dict[index]['id'] == id):
                                    snap_path = snap_list_dict[index]['file_name']
                                    break
                    continue

                if (id is not None):
                    m = re.search('snapshot([0-9]+)\.uid[ ]*=[ ]*"(.*)"', line)
                    if m:
                        index = m.group(1)
                        snap_id = m.group(2)
                        # self.debug_print("Snap ID: {} at Index: {}".format(snap_id, index))
                        snap_list_dict[index].update({'key': index, 'id': snap_id})
                        # try to see if this is the snapshot we are looking for
                        if (snap_id == id):
                            # see if the file name for this snapshot has been filled in
                            if (('file_name') in snap_list_dict[index]):
                                if ((VSPHERE_JSON_DISPLAY_NAME) in snap_list_dict[index]):
                                    if (snap_list_dict[index][VSPHERE_JSON_DISPLAY_NAME] == snap_name):
                                        snap_path = snap_list_dict[index]['file_name']
                                        break
                        continue
        return snap_path

    def _download_snapshot_file(self, snap_name, vmx_path, config, vm, action_result, datacenter, id=None):
        """Function that downloads the suspend file from the esx host

            Args:
                snap_name: The name of the snapshot that is to be downloaded
                vmx_path: The vmx_path of the vm
                config: The config given to the connector
                vm: The pyshpere vm object
                action_result: ActionResult object to update the status to

            Return:
                A status code
        """

        # Progress and config
        server = config[phantom.APP_JSON_SERVER]

        # Downloading the snapshot is a multistep process.
        # All we have is a snapshot name, there is no way to query the API
        # to map this name to a file on disk (of the esx host) YET.
        # So first we need to download the file that contains the snapshot list
        # and info about each snapshot.
        # Parse this file to map the snapshot name to the file_name on disk
        # Then we create a url to the file_name.
        # Then download it.

        # Create the url to the snapshot list file
        snap_list_url = self._create_url_of_file(server, 'snapshotList', vm, datacenter)
        if (not snap_list_url):
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_CANNOT_FIND_SNAPSHOT_LIST_FILE)

        # we will be downloading files for this action, so create a tmp folder for it
        temp_dir = mkdtemp(prefix='vsphere-', dir='/vault/tmp')

        if not os.path.exists(temp_dir):
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_CANNOT_MAKE_TEMP_FOLDER)

        # download the file that contains all the snapshots
        self.save_progress(VSPHERE_PROG_SNAPSHOT_INFO_DOWNLOADING, snap_name=snap_name)
        local_file_path = '{0}/{1}'.format(temp_dir, phantom.get_file_name_from_url(snap_list_url[VSPHERE_CONST_URL]))
        status_code, content_size = self._download_file(snap_list_url, action_result, local_file_path)

        if (phantom.is_fail(status_code)):
            return action_result.get_status()

        # parse the downloaded file and get the file_name that our snapshot represents
        snap_file = self._parse_snap_list_file(local_file_path, snap_name, id)
        if (not snap_file):
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_SNAPSHOT_PATH, snap_name)

        # got the file name, now get the url of this file_name
        snap_file_url = self._create_url_of_file(server, 'snapshotData', vm, datacenter, snap_file)
        if (not snap_file_url):
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_SNAPSHOT_URL, snap_name)

        # Set the status to failure, this is to override the successfull download status of the snapshot list file,
        action_result.set_status(phantom.APP_ERROR)

        os.remove(local_file_path)

        local_file_path = '{0}/{1}-{2}'.format(temp_dir,
                phantom.get_valid_file_name(phantom.get_valid_file_name(snap_name)), phantom.get_file_name_from_url(snap_file_url[VSPHERE_CONST_URL]))

        self.save_progress(VSPHERE_PROG_SNAPSHOT_DOWNLOADING, snap_name=snap_name)
        status_code, content_size = self._download_file(snap_file_url, action_result, local_file_path)
        if (phantom.is_fail(status_code)):
            return action_result.get_status()

        # move it to the vault
        try:
            status_code = self._move_file_to_vault(server, self.get_container_id(), content_size, VSPHERE_CONST_SNAPSHOT_FILE_TYPE,
                    local_file_path, action_result, {VSPHERE_JSON_VMX_PATH: vmx_path}, ["os memory dump", VSPHERE_CONST_SNAPSHOT_FILE_TYPE])

        # remove the temp folder
        finally:
            try:
                os.rmdir(temp_dir)
            except Exception as e:
                self.debug_print('Handled exception', e)
        return action_result.get_status()

    def _download_suspend_file(self, vmx_path, config, action_result, vm, container_id, datacenter):
        """Function that downloads the suspend file from the esx host

            Args:
                vmx_path: The vmx_path of the vm
                config: The config given to the connector
                action_result: ActionResult object to update the status to
                vm: The pyshpere vm object

            Return:
                A status code
        """

        # Init the status to failure
        action_result.set_status(phantom.APP_ERROR)

        # Progress and config
        self.save_progress(VSPHERE_PROG_SUSPEND_FILE_DOWNLOADING)
        server = config[phantom.APP_JSON_SERVER]

        vm_suspend_url = self._create_url_of_file(server, 'suspend', vm, datacenter)

        if (not vm_suspend_url):
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_CANNOT_FIND_SUSPEND_FILE)

        # we will be downloading file for this action, so create a tmp folder for it
        temp_dir = mkdtemp(prefix='vsphere-', dir='/vault/tmp')

        if not os.path.exists(temp_dir):
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_CANNOT_MAKE_TEMP_FOLDER)

        # download it
        local_file_path = '{0}/{1}'.format(temp_dir, phantom.get_file_name_from_url(vm_suspend_url[VSPHERE_CONST_URL]))
        status_code, content_size = self._download_file(vm_suspend_url, action_result, local_file_path)

        if (phantom.is_fail(status_code)):
            return action_result.get_status()

        # move it to the vault
        try:
            status_code = self._move_file_to_vault(server, container_id, content_size, VSPHERE_CONST_SUSPEND_FILE_TYPE,
                local_file_path, action_result, {VSPHERE_JSON_VMX_PATH: vmx_path}, ["os memory dump", VSPHERE_CONST_SUSPEND_FILE_TYPE])
        finally:
            try:
                # remove the temp folder
                os.rmdir(temp_dir)
            except Exception as e:
                self.debug_print('Handled exception', e)
        return action_result.get_status()

    def _get_latest_snapshot_info(self, vm):

        snapshot_list = vm.get_snapshots()

        last_snap_time = 0
        last_snap = None

        for snapshot in snapshot_list:
            create_time = snapshot.get_create_time()
            create_time_secs = mktime(create_time)
            if (last_snap_time < create_time_secs):
                last_snap_time = create_time_secs
                last_snap = snapshot

        if (last_snap):
            self.debug_print('last create time epoch', last_snap_time)
            self.debug_print('last snap name', last_snap.get_name())
            name = last_snap.get_name()
            id = None
            obj_string = last_snap.properties._obj
            m = re.search('.*snapshot-([0-9]+)', obj_string)
            if m:
                id = m.group(1)
            return name, id

        return None, None

    def _handle_take_snapshot(self, action, config, param, container_id):
        """Function that handles ACTION_ID_TAKE_SNAPSHOT

            Args:

            Return:
                A status code
        """

        # Connect to the server
        status_code = self._connect_to_server(config)

        if (phantom.is_fail(status_code)):
            return status_code

        # create an action_result to represent this item
        action_result = self.add_action_result(ActionResult(dict(param)))

        # The path will contain the datacenter also
        datacenter, vmx_path = self._parse_vm_path(param[VSPHERE_JSON_VMX_PATH])

        self.debug_print("datacenter", datacenter)
        self.debug_print("vmx_path", vmx_path)

        # Get the vm object from the vmx path
        try:
            vm = self._vs_server.get_vm_by_path(vmx_path, datacenter)
        except Exception as e:
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_VM_FROM_VMX_PATH, e)

        snap_name = VSPHERE_CONST_SNAPSHOT_NAME_PREFIX + phantom.get_random_chars()
        snap_desc = VSPHERE_CONST_SNAPSHOT_DESCRIPTION.format(container_id=self.get_container_id())

        self.save_progress(VSPHERE_PROG_SNAPSHOT_NAME, snap_name=snap_name)

        task = vm.create_snapshot(snap_name, description=snap_desc, memory=True, sync_run=False)
        status_code = self._wait_for_async_task(task, action, action_result)

        state_not_changed = False

        if (action_result.get_message().find(VSPHERE_VIRTUAL_MACHINE_NOT_CHANGED) != -1):
            state_not_changed = True

        if (phantom.is_fail(status_code) and (not state_not_changed)):
            return status_code
        else:
            message = VSPHERE_VIRTUAL_MACHINE_NOT_CHANGED if (state_not_changed) else VSPHERE_PROG_SNAPSHOT_TAKEN

            self.save_progress(message)
            action_result.set_status(phantom.APP_SUCCESS, message)

        # now check if it needs to be downloaded
        download = bool(param[phantom.APP_JSON_DOWNLOAD]) if (phantom.APP_JSON_DOWNLOAD in param) else True
        if (download):
            # set the action result to failure
            self.set_status(phantom.APP_ERROR)
            id = None
            if (state_not_changed):
                snap_name, id = self._get_latest_snapshot_info(vm)
                if (not snap_name or not id):
                    return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_FAILED_TO_GET_SNAPSHOT_INFO)
                self.debug_print("Latest snapshot: {0} with id {1}".format(snap_name, id))

            status_code = self._download_snapshot_file(snap_name, vmx_path, config, vm, action_result, datacenter, id)

        return action_result.get_status()

    def _revert_snapshot(self, action, config, param):
        """"""

        # Connect to the server
        status_code = self._connect_to_server(config)

        if (phantom.is_fail(status_code)):
            return status_code

        # create an action_result to represent this item
        action_result = self.add_action_result(ActionResult(dict(param)))

        # The path will contain the datacenter also
        datacenter, vmx_path = self._parse_vm_path(param[VSPHERE_JSON_VMX_PATH])

        # Get the vm object from the vmx path
        try:
            vm = self._vs_server.get_vm_by_path(vmx_path, datacenter)
        except Exception as e:
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_VM_FROM_VMX_PATH, e)

        # get the snapshot name
        snap_name = param.get(VSPHERE_JSON_SNAP_NAME)

        if (snap_name is not None):
            task = vm.revert_to_named_snapshot(snap_name, sync_run=False)
        else:
            task = vm.revert_to_snapshot(sync_run=False)

        status_code = self._wait_for_async_task(task, action, action_result)

        if (phantom.is_fail(status_code)):
            return status_code
        else:
            action_result.set_status(phantom.APP_SUCCESS, phantom.APP_SUCC_CMD_EXEC)
            self.save_progress(VSPHERE_PROG_SNAPSHOT_REVERTED)

        return action_result.get_status()

    def _handle_suspend_guest(self, action, config, param, container_id):
        """Function that handles ACTION_ID_SUSPEND_GUEST
            Also downloads the file if config tells it to

            Args:

            Return:
                A status code
        """

        # Connect to the server
        status_code = self._connect_to_server(config)

        if (phantom.is_fail(status_code)):
            return status_code

        # create an action_result to represent this item
        action_result = self.add_action_result(ActionResult(dict(param)))

        # The path will contain the datacenter also
        datacenter, vmx_path = self._parse_vm_path(param[VSPHERE_JSON_VMX_PATH])

        # Get the vm object from the vmx path
        try:
            vm = self._vs_server.get_vm_by_path(vmx_path, datacenter)
        except Exception as e:
            return action_result.set_status(phantom.APP_ERROR, VSPHERE_ERR_VM_FROM_VMX_PATH, e)

        task = None
        # Only suspend if not suspended
        if (not vm.is_suspended()):
            task = vm.suspend(sync_run=False)
            status_code = self._wait_for_async_task(task, action, action_result)
            if (phantom.is_fail(status_code)):
                return status_code
            else:
                action_result.set_status(phantom.APP_SUCCESS, phantom.APP_SUCC_CMD_EXEC)
                self.save_progress(VSPHERE_PROG_SUSPENDED)
        else:
            # Set the status to havent suspended, if file is to be downloaded then it will be overwritten
            self.save_progress(VSPHERE_PROG_SKIPPING_SUSPEND, state=vm.get_status())
            action_result.set_status(phantom.APP_SUCCESS, VSPHERE_SUCC_CANT_EXEC, action=action, state=vm.get_status())

        # either the vm was already suspended or we were able to do it now check if it needs to be downloaded
        download = param[phantom.APP_JSON_DOWNLOAD] if (phantom.APP_JSON_DOWNLOAD in param) else False
        if (download):
            status_code = self._download_suspend_file(vmx_path, config, action_result, vm, container_id, datacenter)

        return action_result.get_status()

    def _test_asset_connectivity(self, config, param):

        if (phantom.is_fail(self._connect_to_server(config))):
            self.debug_print("connect failed")
            self.save_progress(VSPHERE_ERR_CONNECTIVITY_TEST)
            return self.append_to_message(VSPHERE_ERR_CONNECTIVITY_TEST)

        self.debug_print("connect passed")
        self.save_progress(VSPHERE_SUCC_CONNECTIVITY_TEST)
        return self.set_status(phantom.APP_SUCCESS, VSPHERE_SUCC_CONNECTIVITY_TEST)

    def handle_action(self, param):
        """
        """

        result = None
        action = self.get_action_identifier()
        config = self.get_config()
        container_id = self.get_container_id()

        if (action == self.ACTION_ID_GET_REGISTERED_GUESTS) or (action == self.ACTION_ID_GET_RUNNING_GUESTS):
            result = self._get_vms(action, config, param)
        elif(action == self.ACTION_ID_START_GUEST) or (action == self.ACTION_ID_STOP_GUEST):
            result = self._handle_start_stop_guest(action, config, param)
        elif(action == self.ACTION_ID_SUSPEND_GUEST):
            result = self._handle_suspend_guest(action, config, param, container_id)
        elif (action == self.ACTION_ID_TAKE_SNAPSHOT):
            result = self._handle_take_snapshot(action, config, param, container_id)
        elif (action == self.ACTION_ID_REVERT_VM):
            result = self._revert_snapshot(action, config, param)
        elif (action == self.ACTION_ID_GET_SYSTEM_INFO):
            result = self._get_system_info(config, param)
        elif (action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY):
            result = self._test_asset_connectivity(config, param)

        # clean it up
        self._vs_server.disconnect()

        return result

    def handle_exception(self, exception):
        """
        """

        # This throws an exception sometimes stating that server is not connected
        # even when is_connected returns True, could happen if the remote end disconnects.
        try:
            if (self._vs_server.is_connected()):
                    self._vs_server.disconnect()
        except:
            pass


if __name__ == '__main__':

    import sys
    import json
    import pudb
    pudb.set_trace()

    if (len(sys.argv) < 2):
        print "No test json specified as input"
        exit(0)

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = VsphereConnector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print json.dumps(json.loads(ret_val), indent=4)

    exit(0)
