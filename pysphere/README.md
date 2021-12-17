# PySphere

## NOTE

This folder is a modified copy of https://github.com/argos83/pysphere updated to support Python3.

Original documentation is shown below.

## IMPORTANT NOTICE

 * This project has been migrated from http://pysphere.googlecode.com

 * Since 2013 I'm NOT LONGER MAINTAINING this project. I moved to a new country and started working with new technologies so I haven't been able to follow up. Since then a few forks from pysphere have been created and VMWare released its official [python bindings for vSphere](https://developercenter.vmware.com/-/vmware-vsphere-api-python-bindings) that you may want to check out.


## Python API for interacting with the vSphere Web Services SDK.

Visit the [project site](https://github.com/argos83/pysphere) for more information.

**Among other operations, PySphere provides simple interfaces to:**

  - Connect to VMWare's ESX, ESXi, Virtual Center, Virtual Server hosts
  - Query hosts, datacenters, resource pools, virtual machines
  - VMs: Power on, power off, reset, revert to snapshot, get properties, update vmware tools, clone, migrate.
  - vSphere 5.0 Guest Operations:
    - create/delete/move files and directories.
    - upload/download files from the guest system.
    - List/start/stop processes in the guest system.
  - Create and delete snapshots
  - Get hosts statistics and monitor performance

An of course, you can use it to access all the vSphere API through python.

It's built upon a slightly modified version of [ZSI](http://pywebsvcs.sourceforge.net/zsi.html) (that comes bundled-in) which makes it really fast in contrast to other python SOAP libraries that don't provide code generation.

### Installation

The simplest way is using [setuptools](http://pypi.python.org/pypi/setuptools)' easy_install:

```
easy_install -U pysphere
```

Or using [pip](http://pypi.python.org/pypi/pip):

```
pip install -U pysphere
```

You can aslo find the source package and windows installer in the [downloads](http://code.google.com/p/pysphere/downloads/list) section. To install it from the source package:

1. Unzip the package
2. run: `python setup.py install`

### Quick Example

Here's how you power on a virtual machine. See also the [getting started guide](http://code.google.com/p/pysphere/wiki/GettingStarted) and the project's [wiki](http://code.google.com/p/pysphere/w/list) with the full documentation.

```
>>> from pysphere import VIServer
>>> server = VIServer()
>>> server.connect("my.esx.host.com", "myusername", "secret")
>>> vm = server.get_vm_by_path("[datastore] path/to/file.vmx")
>>> vm.power_on()
>>> print vm.get_status()
POWERED ON
```

### Discussion Group

You can find a lot more examples and use cases in the [discussion group](http://groups.google.com/group/pysphere).

### License

```
Copyright (c) 2012, Sebastian Tello
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
  * Neither the name of copyright holders nor the names of its contributors
    may be used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```


### ZSI License

```
Copyright (c) 2003, The Regents of the University of California,
through Lawrence Berkeley National Laboratory (subject to receipt of
any required approvals from the U.S. Dept. of Energy). All rights
reserved. Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:

(1) Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
(2) Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
(3) Neither the name of the University of California, Lawrence Berkeley
National Laboratory, U.S. Dept. of Energy nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.

You are under no obligation whatsoever to provide any bug fixes,
patches, or upgrades to the features, functionality or performance of
the source code ("Enhancements") to anyone; however, if you choose to
make your Enhancements available either publicly, or directly to
Lawrence Berkeley National Laboratory, without imposing a separate
written license agreement for such Enhancements, then you hereby grant
the following license: a non-exclusive, royalty-free perpetual license
to install, use, modify, prepare derivative works, incorporate into
other computer software, distribute, and sublicense such Enhancements
or derivative works thereof, in binary and source code form.
```
