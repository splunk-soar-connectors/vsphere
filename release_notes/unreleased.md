**Unreleased**
* Replaced pysphere with pyVmomi to resolve FIPS 140-3 compliance violations
* Fixed scoped SSL context — certificate verification no longer globally disabled when `verify_server_cert` is false
* Changed `verify_server_cert` default to `true`
* Updated minimum supported ESXi version to 6.5 (required by pyVmomi 9.x)
* Set `fips_compliant` to `false` pending validation on a FIPS 140-3 enabled instance
