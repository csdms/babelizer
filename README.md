# bmi_wrap
Wrap BMI models with Python bindings

# Examples

Generate Python bindings for a C library that implements a BMI,

```bash
$ bmi wrap libbmi_sedflux3d.dylib \
      --module-name=sedflux3d \
      --bmi-include=sedflux3d/bmi_sedflux3d.h \
      --bmi-register=register_bmi_sedflux3d
```
Arguments can also be stored in a file and the file passed to bmi-wrap,
```
$ bmi wrap @args.txt
```
The argument file simply lists arguments one-per-line,
```
# args.txt
libbmi_sedflux3d.dylib
--module-name=sedflux3d
--bmi-include=sedflux3d/bmi_sedflux3d.h
--bmi-register=register_bmi_sedflux3d
```
