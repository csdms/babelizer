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


The babelizer is a command-line utility that generates Python code
to bring libraries from other languages into Python. Target libraries
must expose a Basic Model Interface (BMI; @peckham:2013, @hutton:2020) and be written in
C, C++, or Fortran. We have made the babelizer extendable and so
additional languages can be added in the future. This provides a
streamlined way to bring scientific models into a common language
where they can communicate with one another as components of an integrated model.

Scientific modeling has increasingly moved to an integrated
multicomponent modeling approach. With such an approach, scientific
modelers -- not just software developers -- connect model components
to one another to form larger, integrated, models where plug-and-play
components can easily be swapped-out, added or removed. This is in
contrast to older methods where a single modeling group constructs
a monolithic model built on the tight integration of software written
within a single framework. A single person or group would tightly
control model development and outside contributions would go through
a gatekeeper to ensure compatibility. The smaller software elements
that make up the model are tightly tied to the larger model and,
generally, not used outside of this framework.

Component modeling democratizes model building. The scientific
modeling community develops model components, which allows for
more efficient and powerful model development that is driven
from the bottom-up by a community. This reduces redundancy -- rather
than reinventing software, scientists are able to pick up and
use other models that suit their needs -- and allows scientists
to focus on new, unsolved, problems. There are disadvantages, however.

Without a single group to guide model development, there is a
greater risk that community-developed models will become incompatible
with one another. With hundreds of scientists developing models in
isolation, there is a greater likelihood models will be written with
idiosyncratic designs, incompatible grids, incompatible time steps,
and even in different programming languages. The Earth-system modeling
community has developed tools to help solve some of these problems.
For example, the Basic Model Interface (BMI) defines an interface that
standardizes model design. The ESMF grid mappers are able to map
quantities from one grid to another. The pymt helps with time
interpolation (there are other tools as well, I just need to find
them). In this paper we describe a solution to solve the language
incompatibility problem.

To get an idea of the range of programming languages used in Earth
modeling, we can look to the Community Surface Dynamics Modeling
repository. The repository currently holds over 370 open source
models of the community (as of June 2020). The models and tools in
the repository span a range of languages, with Python, C, and Fortran
being the most popular (Figure 1). The diversity of languages raises
a challenge in creating an interoperable framework. Our solution is
to use a hub-and-spoke approach where Python acts as the hub that
connects to other languages. Using the CSDMS model repository as a
guide, we see that if we build translators for the most popular Open
Source languages (C, C++, Fortran, and Python) we will cover 80% of
the contributed models.

We have built the babelizer to generate the spokes that connect
the hub language, Python, to other languages. We chose Python as
the hub because of its popularity in the scientific community,
its extensive collection of third-party libraries (including model
coupling frameworks such as the pymt), and its existing ability to
communicate with other programming languages. A drawback of using
Python is that it can be relatively slow -- as compared to compiled
languages like C and Fortran -- however, the models being wrapped
are compiled and run in their native languages, which is where
the bulk of the computation takes place, with the babelizer providing
only a thin wrapper layer.

The babelizer is a command-line utility that generates the glue code
to bring a model that exposes a BMI from another language into Python.
Because the BMI is a well-defined standard, the babelizer requires
only a small amount of metadata to generate the glue code. The metadata
depends somewhat on the language being wrapped but includes the name
of the library providing the BMI, the name of an entry point into the
library, the language the library was written in, and any necessary
compiler flags. With this metadata, the babelizer creates a new git
repository, a python package containing the Python interface to the
model, documentation, and sets up continuous integrations and a test
suite for the model’s BMI. The model can now be imported and run
through Python.

The user provides metadata describing his or her model through a
toml-formatted file (see Figure 1 for an example). The babelizer uses
the metadata to fill a set of jinja-formatted template files to construct
the new repository (or update an existing repository). The entire
repository is almost completely auto-generated -- and so can easily
be regenerated -- the only files a user should edit are the main
configuration file, babel.toml, and any optional model data files,
which will be installed along with the new component.

Data files provided to the babelized component are intended to
be used either by a user of the new component or by a separate
framework that imports the component. There is little restriction
on the contents of the files but, typically, they are sample input
files that a user of the component can use to run the model.
Another use-case is where the component will be used within a
separate modeling framework and that framework may require additional
metadata. As an example, the Python Modeling Toolkit (pymt) is a
modeling framework able to work with generic BMI models. In addition
to the BMI, the pymt requires descriptive information about the model
(e.g. authors, license, references, summary of what it does, etc.)
as well as jinja-formatted sample input files. The pymt uses the
template input files as part of a utility for a user to programmatically
generate model input files without having to know anything about
idiosyncratic details of model input files. Within such a framework,
therefore, a user is given model components with a standardized way
to create input files, as well as a common, Python, interface to
run and interact with the model.


# Acknowledgements

This work is supported by the National Science Foundation
under Grant No. 1831623, *Community Facility Support: The
Community Surface Dynamics Modeling System (CSDMS)*.

# References


