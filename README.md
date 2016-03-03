# vsphere helper
Added vsphere_helper.py as the commandline interface

<pre>
usage: vsphere_helper.py [-h] [-a VAPPNAME] [-s SNAPNAME]

                         [{list,createsnapshot,revertsnapshot,deletesnapshot,ip,poweron,poweroff}]

positional arguments:
  {list,createsnapshot,revertsnapshot,deletesnapshot,ip,poweron,poweroff}
                        operation to take, default is list

optional arguments:
  -h, --help            show this help message and exit
  -a VAPPNAME, --vappname VAPPNAME
                        vpp name
  -s SNAPNAME, --snapname SNAPNAME
                        snapshot name
  --confirmed           confirm the arguments without interaction
</pre>
