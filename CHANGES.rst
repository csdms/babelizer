Changelog
=========

.. towncrier release notes start

0.3.8 (2021-05-03)
------------------

Bugfixes
""""""""

- Fix minor formatting issues in rendered output. (`#49
  <https://github.com/csdms/babelizer/issues/49>`_)


Improved Documentation
""""""""""""""""""""""

- Update docs for API changes. (`#47
  <https://github.com/csdms/babelizer/issues/47>`_)


0.3.7 (2021-03-19)
------------------

Features
""""""""

- Render GitHub Actions for continuous integration of the generated projects.
  (`#41 <https://github.com/csdms/babelizer/issues/41>`_)


Misc
""""

- Use GitHub Actions for continuous integration. (`#39
  <https://github.com/csdms/babelizer/issues/39>`_)


0.3.6 (2021-01-13)
------------------

Bugfixes
""""""""

- Fixed issue with metadata install path for Python components. (`#36
  <https://github.com/csdms/babelizer/issues/36>`_)


0.3.5 (2020-12-16)
------------------

Misc
""""

- Removed use of the toml package, instead use tomlkit. (`#34
  <https://github.com/csdms/babelizer/issues/34>`_)


0.3.4 (2020-12-16)
------------------

Bugfixes
""""""""

- Fixed a templating problem that caused Python BMIs to fail to build. (`#33
  <https://github.com/csdms/babelizer/issues/33>`_)


Improved Documentation
""""""""""""""""""""""

- Minor edits to README and CLI help strings. (`#29
  <https://github.com/csdms/babelizer/issues/29>`_)
- Added text on the CSDMS Workbench to the README and docs. (`#30
  <https://github.com/csdms/babelizer/issues/30>`_)
- Clarified text in docs example. (`#31
  <https://github.com/csdms/babelizer/issues/31>`_)


Misc
""""

- Included the Python BMI example in the test suite.. (`#33
  <https://github.com/csdms/babelizer/issues/33>`_)


0.3.3 (2020-10-31)
------------------

Features
""""""""

- Added missing methods, primarily for unstructured grids, to C and C++
  implementation. (`#28 <https://github.com/csdms/babelizer/issues/28>`_)


Bugfixes
""""""""

- Fixed a rendering error that caused import lines to run together when
  wrapping multiple components (`#28
  <https://github.com/csdms/babelizer/issues/28>`_)


Misc
""""

- Removed Python 3.6 builds. (`#28 <https://github.com/csdms/babelizer/issues/28>`_)


0.3.2 (2020-10-08)
------------------

Bugfixes
""""""""

- Fix babelizing C++ libraries and added tests for C++ babelizing.  This fix
  necessitated a change to the "library" section of the babel.toml
  configuration file. (`#26
  <https://github.com/csdms/babelizer/issues/26>`_)


0.3.1 (2020-09-25)
------------------

Improved Documentation
""""""""""""""""""""""

- Automatically set version in docs from the package version. (`#23 <https://github.com/csdms/babelizer/issues/23>`_)


0.3.0 (2020-09-24)
------------------

Improved Documentation
""""""""""""""""""""""

- Added a user guide and API documentation (`#21 <https://github.com/csdms/babelizer/issues/21>`_)


0.2.0 (2020-09-10)
------------------

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


0.1.3 (2018-10-28)
------------------

- Added new ``bmi-render`` command. The old ``bmi-wrap`` command is still available
  but will be removed in future releases.


0.1.2 (2018-06-28)
------------------

- Added update_until BMI method for C++.

- Fixed BMI return values for C.


0.1.1 (2018-04-09)
------------------

- Added continuous integration with Travis-CI. Build on Linux/MacOS with
  Python 2.7, 3.4, 3.5, 3.6.


0.1.0 (2018-04-05)
------------------

- Initial release

