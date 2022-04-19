[comment]: # "Auto-generated SOAR connector documentation"
# vSphere

Publisher: Splunk  
Connector Version: 2\.0\.5  
Product Vendor: VMware  
Product Name: vSphere  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.1\.0  

This app implements investigative, containment and VM management actions on VMware ESXi or vCenter server

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2016-2022 Splunk Inc."
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""
## pysphere

This app uses the pysphere module, which is licensed under the New BSD License. Copyright (c) 2012,
Sebastian Tello All rights reserved.


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a vSphere asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**server** |  required  | string | Server IP/Hostname
**verify\_server\_cert** |  optional  | boolean | Verify server certificate
**username** |  required  | string | Administrator username
**password** |  required  | password | Administrator password

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity\. This action logs into the device to check the connection and credentials  
[list vms](#action-list-vms) - Get the list of registered VMs  
[get system info](#action-get-system-info) - Get information about a VM  
[start vm](#action-start-vm) - Start a stopped or suspended VM  
[revert vm](#action-revert-vm) - Revert VM to a named snapshot if name is specified, otherwise revert to the current snapshot  
[stop vm](#action-stop-vm) - Stop a VM  
[suspend vm](#action-suspend-vm) - Suspend a VM  
[snapshot vm](#action-snapshot-vm) - Take a snapshot of the VM  

## action: 'test connectivity'
Validate the asset configuration for connectivity\. This action logs into the device to check the connection and credentials

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'list vms'
Get the list of registered VMs

Type: **investigate**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.data\.\*\.ip | string |  `ip` 
action\_result\.data\.\*\.state | string | 
action\_result\.data\.\*\.vm\_full\_name | string | 
action\_result\.data\.\*\.vm\_hostname | string |  `host name` 
action\_result\.data\.\*\.vm\_name | string | 
action\_result\.data\.\*\.vmx\_path | string |  `vm` 
action\_result\.summary\.running\_vms | numeric | 
action\_result\.summary\.total\_vms | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get system info'
Get information about a VM

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip\_hostname** |  required  | Hostname/IP address to get info of | string |  `host name`  `ip` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.ip\_hostname | string |  `host name`  `ip` 
action\_result\.data\.\*\.ip | string |  `ip` 
action\_result\.data\.\*\.state | string | 
action\_result\.data\.\*\.vm\_full\_name | string | 
action\_result\.data\.\*\.vm\_hostname | string |  `host name` 
action\_result\.data\.\*\.vm\_name | string | 
action\_result\.data\.\*\.vmx\_path | string |  `vm` 
action\_result\.summary\.found\_endpoint | boolean | 
action\_result\.summary\.total\_vms\_searched | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'start vm'
Start a stopped or suspended VM

Type: **correct**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**vmx\_path** |  required  | VMX file path | string |  `vm` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.vmx\_path | string |  `vm` 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'revert vm'
Revert VM to a named snapshot if name is specified, otherwise revert to the current snapshot

Type: **contain**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**vmx\_path** |  required  | VMX file path | string |  `vm` 
**snapshot** |  optional  | Snapshot name \(case sensitive\) to revert to | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.snapshot | string | 
action\_result\.parameter\.vmx\_path | string |  `vm` 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'stop vm'
Stop a VM

Type: **contain**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**vmx\_path** |  required  | VMX file path | string |  `vm` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.vmx\_path | string |  `vm` 
action\_result\.data | string | 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'suspend vm'
Suspend a VM

Type: **contain**  
Read only: **False**

The <b>start vm</b> action can be used to resume a suspended vm\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**vmx\_path** |  required  | VMX file path | string |  `vm` 
**download** |  optional  | Download suspend file to the vault | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.download | boolean | 
action\_result\.parameter\.vmx\_path | string |  `vm` 
action\_result\.data\.\*\.host | string |  `ip` 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.size | string | 
action\_result\.data\.\*\.type | string | 
action\_result\.data\.\*\.vault\_id | string |  `vault id`  `os memory dump`  `vm suspend file` 
action\_result\.data\.\*\.vmx\_path | string |  `vm` 
action\_result\.summary | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'snapshot vm'
Take a snapshot of the VM

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**vmx\_path** |  required  | VMX file path | string |  `vm` 
**download** |  optional  | Download snapshot file to the vault | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.download | boolean | 
action\_result\.parameter\.vmx\_path | string |  `vm` 
action\_result\.data\.\*\.host | string |  `ip` 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.size | string | 
action\_result\.data\.\*\.type | string | 
action\_result\.data\.\*\.vault\_id | string |  `vault id`  `os memory dump`  `vm snapshot file` 
action\_result\.data\.\*\.vmx\_path | string |  `vm` 
action\_result\.summary | string | 
action\_result\.message | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 