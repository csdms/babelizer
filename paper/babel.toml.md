<!-- Source: https://github.com/pymt-lab/pymt_prms_surface/blob/master/babel.toml -->

```toml
[library]
[library.PRMSSurface]
language = "fortran"
library = "bmiprmssurface"
header = ""
entry_point = "bmi_prms_surface"

[build]
undef_macros = []
define_macros = []
libraries = []
library_dirs = []
include_dirs = []
extra_compile_args = []

[package]
name = "pymt_prms_surface"
requirements = ["prms", "prms_surface"]

[info]
github_username = "pymt-lab"
package_author = "Community Surface Dynamics Modeling System"
package_author_email = "csdms@colorado.edu"
package_license = "MIT"
summary = "PRMS6 surface water process component"

[ci]
python_version = ["3.9"]
os = ["linux", "mac", "windows"]
```
