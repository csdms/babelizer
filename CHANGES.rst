=======================
Changelog for babelizer
=======================

******************
0.3.9 (unreleased)
******************

- Allow user to set default branch name (#60)
- Improve the readme docs (#57)
- Update tests and generate coverage (#56)
- Complete API documentation (#55)


******************
0.3.8 (2021-05-03)
******************

- Update docs for API changes (#47)
- Fix minor formatting issues in rendered output (#49)


******************
0.3.7 (2021-03-19)
******************

- Render GitHub Actions for continuous integration of the generated
  projects (#41)

- Use GitHub Actions for continuous integration (#39)


******************
0.3.6 (2021-01-13)
******************

- Fixed issue with metadata install path for Python components (#36)

- Minor edits to README


******************
0.3.5 (2020-12-16)
******************

- Removed use of the toml package, instead use tomlkit (#34)


******************
0.3.4 (2020-12-16)
******************

- Minor edits to README and CLI help strings (#29)

- Added text on the CSDMS Workbench to the README and docs (#30)

- Clarified text in docs example (#31)

- Fixed a templating problem that caused Python BMIs to fail to build.
  Included the Python BMI example in the test suite. (#33)


******************
0.3.3 (2020-10-31)
******************

- Added missing methods, primarily for unstructured grids, to C and C++
  implementation (#28)

- Fixed a rendering error that caused import lines to run together
  when wrapping multiple components (#28)

- Removed Python 3.6 builds (#28)


******************
0.3.2 (2020-10-08)
******************

- Fix babelizing C++ libraries and added tests for C++ babelizing.
  This fix necessitated a change to the "library" section
  of the babel.toml configuration file. (#26)


******************
0.3.1 (2020-09-25)
******************

- Automatically set version in docs from the package version. (#23)


******************
0.3.0 (2020-09-24)
******************

- Added user guide and API documentation (#21)


******************
0.2.0 (2020-09-10)
******************

- Improved testing of the babelizer and added the bmi_heat C library to use for
  testing babelizing a package. (#20)

- Updated the babelized package for C libraries to BMI 2. (#20)

- Moved the external cookiecutter template into ``babelizer`` package.

- Renamed package to ``babelizer``.

- Added ``init``, ``update``, and ``quickstart`` subcommands to the babelize cli.

- Updated to use the new isort v5 api.

- Changed to use toml format by default for config files. The old yaml
  format is still understood but is deprecated.

- Fixed a bug where ``git init`` was called from the parent directory
  of the newly-created project, rather than from within the project.

- Removed versioneer from the babelized package. The version is now
  maintained within setup.py and releases should be made using
  zest.releaser.


******************
0.1.3 (2018-10-28)
******************

- Added new ``bmi-render`` command. The old ``bmi-wrap`` command is still available
  but will be removed in future releases.


******************
0.1.2 (2018-06-28)
******************

- Added update_until BMI method for C++.

- Fixed BMI return values for C.


******************
0.1.1 (2018-04-09)
******************

- Added continuous integration with Travis-CI. Build on Linux/MacOS with
  Python 2.7, 3.4, 3.5, 3.6.


******************
0.1.0 (2018-04-05)
******************

- Initial release

