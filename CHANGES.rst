Changelog for babelizer
=======================

0.2.0 (unreleased)
-------------------

- Moved the external cookiecutter template into ``babelizer`` package.

- Renamed package to ``babelizer``.

- Added ``init``, ``update``, and ``quickstart`` subcommands to the babelize cli.

- Updated to use the new isort v5 api.

- Changed to use toml format by default for config files. The old yaml
  format is still understood but is deprecated.

- Fixed a bug where ``git init`` was called from the parent directory
  of the newly-created project, rather than from within the project.


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

