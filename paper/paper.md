---
title: "The Babelizer"
tags:
  - C
  - C++
  - Fortran
  - Python
  - geosciences
  - modeling
  - interface
authors:
  - name: Eric W.H. Hutton
    orcid: 0000-0002-5864-6459
    affiliation: 1
  - name: Mark D. Piper
    orcid: 0000-0001-6418-277X
    affiliation: 1
  - name: Gregory E. Tucker
    orcid: 0000-0003-0364-5800
    affiliation: 1, 2, 3
affiliations:
  - name: Community Surface Dynamics Modeling System, University of Colorado Boulder
    index: 1
  - name: Cooperative Institute for Research in Environmental Sciences (CIRES), University of Colorado Boulder
    index: 2
  - name: Department of Geological Sciences, University of Colorado Boulder
    index: 3
date: 18 December 2020
bibliography: paper.bib

---

# Summary

The `babelizer` is a Python utility that generates code
to import libraries from other languages into Python. Target libraries
must expose a Basic Model Interface (BMI; @hutton:2020b, @peckham:2013) and be written in
C, C++, or Fortran, although the `babelizer` is extendable, so
other languages can be added in the future. The `babelizer` provides a
streamlined mechanism for bringing scientific models into a common language
where they can communicate with one another as components of an integrated model.


# Statement of need

With an integrated multicomponent approach to modeling, scientific
modelers--not just software developers--connect components
to form integrated models, where plug-and-play
components can easily be added or removed (@tucker:2021, @david:2013, gregersen:2007, @collins:2005).
This is in contrast to older methods, where a single modeling group would construct
a monolithic model built on the tight integration of software written
within an isolated framework. A single person or group would
control model development. Outside contributors would go through
a gatekeeper to ensure compatibility. The software elements
that made up the model would be tied to the larger model and,
generally, not used outside of the framework.

Component modeling democratizes model building by empowering the larger scientific
community to develop model components. This allows for
more innovation and experimentation driven
from the bottom up by a community. It reduces redundancy--rather
than reinventing software, scientists can find and
use models that suit their needs--and it allows scientists
to focus on new, unsolved, problems. 

There are disadvantages, however.
Without a single group to guide model development, there is a
greater risk that community-developed models will become incompatible
with one another. With hundreds of scientists developing models in
isolation, there is a greater likelihood models will be written with
idiosyncratic designs, incompatible grids, incompatible time steps,
and even in different programming languages. The Earth-system modeling
community has developed tools to help solve some of these problems.
For example, the Basic Model Interface
standardizes model interactions. The Earth System Modeling Framework (ESMF) [@collins:2005]
grid mappers are able to map quantities from one grid to another.
The Python Modeling Toolkit `pymt` [@hutton:2020a] performs time
interpolation, grid mapping, and unit coversion.
In this paper, we present a solution to the language incompatibility problem.

## Overcoming the language incompatibility problem

To get an idea of the range of programming languages used in Earth-system
modeling, we can look to the Community Surface Dynamics Modeling System (CSDMS)
model repository. As of June 2020, the repository holds over 370 open source
models and tools submitted by the community. These contributions span a range of languages, with Python, C, and Fortran
being the most popular (Figure 1).
The mix of languages raises
an interesting challenge in creating an interoperable modeling framework.
Our solution is to use a hub-and-spoke approach, where Python is the hub language that
connects to other languages.
We chose Python as
the hub because of its popularity in the scientific community,
its extensive collection of third-party libraries (including model
coupling frameworks such as the `pymt`), and its existing ability to
communicate with other programming languages.
We have built the `babelizer` to generate the spokes that connect Python to other languages.
Using the CSDMS model repository as a
guide, if we build translators for the open
source languages C, C++, Fortran, and Python, we will cover 80 percent of
the contributed models.
A drawback of using
Python is that it can be relatively slow compared to compiled
languages like C and Fortran; however, the models being wrapped
are compiled and run in their native language, which is where
the bulk of the computation takes place, with the `babelizer` providing
only a thin wrapper layer.


# Design of the babelizer

The `babelizer` is a command-line utility that generates the glue code
to bring a model exposing a BMI from another language into Python.
Because the BMI is a well-defined standard, the `babelizer` requires
only a small amount of metadata to generate the glue code. The metadata
depends somewhat on the language being wrapped, but includes the name
of the library providing the BMI, the name of an entry point into the
library, the language the library was written in, and any necessary
compiler flags. With this metadata, the `babelizer` creates a new `git`
repository, a Python package containing the Python interface to the
model, documentation, and sets up continuous integrations and a test
suite for the model’s BMI. The model can then be imported and run
through Python.

The user provides metadata describing their model through a
*toml*-formatted file (see Figure 2 for an example). The `babelizer` uses
the metadata to fill a set of *jinja*-formatted template files to construct
the new repository (or update an existing repository). The entire
repository is almost completely auto-generated, which means it can easily
be regenerated. The only files a user need edit are the main
configuration file, `babel.toml`, and any optional model data files,
which are installed along with the new component.

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
github_username = "csdms"
package_author = "Community Surface Dynamics Modeling System"
package_author_email = "csdms@colorado.edu"
package_license = "MIT"
summary = "PRMS6 surface water process component"
```
*Figure 2:
The `babelizer` configuration file (`babel.toml`)
for the Precipitation-Runoff Modeling System v6
surface water component, `PRMSSurface` (@piper:2020).
Running the `babelizer` on this file produces most of
the repository https://github.com/pymt-lab/pymt_prms_surface.*

Data files provided to a babelized component are intended to
be used either by a user of the new component or by a separate
framework that imports the component. There is little restriction
on the contents of the files, but typically they are sample input
files that a user of the component can use to run the model.
Another use-case is where the component will be used within a
separate modeling framework and that framework may require additional
metadata. As an example, the `pymt` is a
modeling framework able to work with generic BMI models. In addition
to the BMI, the `pymt` requires descriptive information about the model
(e.g. authors, license, references, summary of what it does, etc.)
as well as *jinja*-formatted sample input files. The `pymt` uses the
template input files as part of a utility for a user to programmatically
generate model input files without having to know anything about the
idiosyncratic details of those model input files. Within such a framework,
therefore, a user is given model components with a standardized way
to create input files, as well as a common Python interface to
run and interact with the model.


# Acknowledgements

This work is supported by the National Science Foundation
under Grant No. 1831623, *Community Facility Support: The
Community Surface Dynamics Modeling System (CSDMS)*.

# References


