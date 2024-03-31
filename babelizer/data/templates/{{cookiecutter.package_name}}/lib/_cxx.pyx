# cython: c_string_type=str, c_string_encoding=ascii

import ctypes

cimport numpy as np
from libcpp.string cimport string
from libcpp.vector cimport vector

import numpy as np
{%- for babelized_class, component in cookiecutter.components|dictsort %}

# start: {{ babelized_class|lower }}.pyx

cdef extern from "{{ component.header }}":
    cdef cppclass {{ component.entry_point }}:
        Model() except +

        #  Model control functions.
        void Initialize(string config_file) except +
        void Update()
        void UpdateUntil(double time)
        void Finalize()

        #  Model information functions.
        string GetComponentName()
        int GetInputItemCount()
        int GetOutputItemCount()
        vector[string] GetInputVarNames()
        vector[string] GetOutputVarNames()

        #  Variable information functions
        int GetVarGrid(string name)
        string GetVarType(string name)
        string GetVarUnits(string name)
        int GetVarItemsize(string name)
        int GetVarNbytes(string name)
        string GetVarLocation(string name)

        double GetCurrentTime()
        double GetStartTime()
        double GetEndTime()
        string GetTimeUnits()
        double GetTimeStep()

        #  Variable getters
        void GetValue(string name, void *dest)
        void *GetValuePtr(string name)
        void GetValueAtIndices(string name, void *dest, int *inds, int count)

        #  Variable setters
        void SetValue(string name, void *src)
        void SetValueAtIndices(string name, int *inds, int count, void *src)

        #  Grid information functions
        int GetGridRank(const int grid)
        int GetGridSize(const int grid)
        string GetGridType(const int grid)

        void GetGridShape(const int grid, int *shape)
        void GetGridSpacing(const int grid, double *spacing)
        void GetGridOrigin(const int grid, double *origin)

        void GetGridX(const int grid, double *x)
        void GetGridY(const int grid, double *y)
        void GetGridZ(const int grid, double *z)

        int GetGridNodeCount(const int grid)
        int GetGridEdgeCount(const int grid)
        int GetGridFaceCount(const int grid)

        void GetGridEdgeNodes(const int grid, int *edge_nodes)
        void GetGridFaceEdges(const int grid, int *face_edges)
        void GetGridFaceNodes(const int grid, int *face_nodes)
        void GetGridNodesPerFace(const int grid, int *nodes_per_face)

cdef class {{ babelized_class }}:
    cdef {{ component.entry_point }} _bmi

    METADATA = "../data/{{ babelized_class }}"

    def __cinit__(self):
        pass

    def buffer(self):
        return <bytes>self.STR_BUFFER

    def initialize(self, config_file):
        self._bmi.Initialize(config_file)

    def update(self):
        self._bmi.Update()

    def update_until(self, time):
        self._bmi.UpdateUntil(time)

    def finalize(self):
        self._bmi.Finalize()

    cpdef int get_var_grid(self, name):
        return self._bmi.GetVarGrid(<char*>name)

    cpdef string get_var_type(self, name):
        return self._bmi.GetVarType(<char*>name)

    cpdef string get_var_units(self, name):
        return self._bmi.GetVarUnits(<char*>name)

    cpdef int get_var_itemsize(self, name):
        return self._bmi.GetVarItemsize(<char*>name)

    cpdef int get_var_nbytes(self, name):
        return self._bmi.GetVarNbytes(<char*>name)

    cpdef string get_var_location(self, name):
        return self._bmi.GetVarLocation(<char*>name)

    cpdef string get_component_name(self):
        return self._bmi.GetComponentName()

    cpdef int get_input_var_name_count(self):
        return self._bmi.GetInputItemCount()

    cpdef int get_output_var_name_count(self):
        return self._bmi.GetOutputItemCount()

    def get_input_var_names(self):
        return tuple(self._bmi.GetInputVarNames())

    def get_output_var_names(self):
        return tuple(self._bmi.GetOutputVarNames())

    cpdef double get_current_time(self):
        return self._bmi.GetCurrentTime()

    cpdef double get_start_time(self):
        return self._bmi.GetStartTime()

    cpdef double get_end_time(self):
        return self._bmi.GetEndTime()

    cpdef string get_time_units(self):
        return self._bmi.GetTimeUnits()

    cpdef double get_time_step(self):
        return self._bmi.GetTimeStep()

    cpdef get_value(self, name, np.ndarray buff):
        self._bmi.GetValue(<char*>name, buff.data)
        return buff

    cpdef set_value(self, name, np.ndarray buff):
        self._bmi.SetValue(<char*>name, buff.data)
        return buff

    cpdef int get_grid_rank(self, gid):
        return self._bmi.GetGridRank(gid)

    cpdef int get_grid_size(self, gid):
        return self._bmi.GetGridSize(gid)

    cpdef int get_grid_node_count(self, gid):
        return self._bmi.GetGridNodeCount(gid)

    cpdef int get_grid_edge_count(self, gid):
        return self._bmi.GetGridEdgeCount(gid)

    cpdef int get_grid_face_count(self, gid):
        return self._bmi.GetGridFaceCount(gid)

    cpdef string get_grid_type(self, gid):
        return self._bmi.GetGridType(gid)

    cpdef get_grid_shape(self, gid, np.ndarray[int, ndim=1] shape):
        self._bmi.GetGridShape(gid, &shape[0])
        return shape

    cpdef get_grid_spacing(self, gid, np.ndarray[double, ndim=1] spacing):
        self._bmi.GetGridSpacing(gid, &spacing[0])
        return spacing

    cpdef get_grid_origin(self, gid, np.ndarray[double, ndim=1] origin):
        self._bmi.GetGridOrigin(gid, &origin[0])
        return origin

    cpdef get_grid_x(self, gid, np.ndarray[double, ndim=1] buff):
        self._bmi.GetGridX(gid, &buff[0])
        return buff

    cpdef get_grid_y(self, gid, np.ndarray[double, ndim=1] buff):
        self._bmi.GetGridY(gid, &buff[0])
        return buff

    cpdef get_grid_z(self, gid, np.ndarray[double, ndim=1] buff):
        self._bmi.GetGridZ(gid, &buff[0])
        return buff

    cpdef get_grid_face_nodes(self, gid, np.ndarray[int, ndim=1] buff):
        self._bmi.GetGridFaceNodes(gid, &buff[0])
        return buff

    cpdef get_grid_nodes_per_face(self, gid, np.ndarray[int, ndim=1] buff):
        self._bmi.GetGridNodesPerFace(gid, &buff[0])
        return buff

    cpdef get_grid_edge_nodes(self, gid, np.ndarray[int, ndim=1] buff):
        self._bmi.GetGridEdgeNodes(gid, &buff[0])
        return buff
{% endfor %}
