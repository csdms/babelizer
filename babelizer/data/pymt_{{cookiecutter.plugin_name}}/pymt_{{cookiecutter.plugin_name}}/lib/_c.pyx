# cython: c_string_type=str, c_string_encoding=ascii

import ctypes
from libc.stdlib cimport malloc, free

cimport numpy as np
import numpy as np


SIZEOF_FLOAT = 8 * ctypes.sizeof(ctypes.c_float)
SIZEOF_DOUBLE = 8 * ctypes.sizeof(ctypes.c_double)
SIZEOF_INT = 8 * ctypes.sizeof(ctypes.c_int)
SIZEOF_LONG = 8 * ctypes.sizeof(ctypes.c_long)


DTYPE_C_TO_PY = {
    'float': 'float{bits}'.format(bits=SIZEOF_FLOAT),
    'double': 'float{bits}'.format(bits=SIZEOF_DOUBLE),
    'int': 'int{bits}'.format(bits=SIZEOF_INT),
    'long': 'int{bits}'.format(bits=SIZEOF_LONG),
}


cdef extern from "bmi.h":
    ctypedef struct BMI_Model:
        pass


cdef extern from "bmi.c":
    BMI_Model* bmi_new()

    int bmi_initialize(BMI_Model* model, const char *config_file)
    int bmi_update(BMI_Model* model)
    int bmi_update_until(BMI_Model* model, double until)
    # int bmi_update_frac(BMI_Model* model, double frac)
    int bmi_finalize(BMI_Model* model)
    # int bmi_run_model(BMI_Model* model)

    int bmi_get_component_name(BMI_Model* model, char* name)
    int bmi_get_input_item_count(BMI_Model* model, int *count)
    int bmi_get_output_item_count(BMI_Model* model, int *count)

    int bmi_get_input_var_names(BMI_Model* model, char **names)
    int bmi_get_output_var_names(BMI_Model* model, char **names)

    int bmi_get_var_grid(BMI_Model* model, const char *name, int *gid)
    int bmi_get_var_type(BMI_Model* model, const char *name, char *dtype)
    int bmi_get_var_units(BMI_Model* model, const char *name, char *units)
    int bmi_get_var_itemsize(BMI_Model* model, const char *name, int *itemsize)
    int bmi_get_var_nbytes(BMI_Model* model, const char *name, int *nbytes)
    int bmi_get_var_location(BMI_Model* model, const char *name, char *location)

    int bmi_get_current_time(BMI_Model* model, double* time)
    int bmi_get_start_time(BMI_Model* model, double* time)
    int bmi_get_end_time(BMI_Model* model, double* time)
    int bmi_get_time_units(BMI_Model* model, char* units)
    int bmi_get_time_step(BMI_Model* model, double* time)

    int bmi_get_value(BMI_Model* model, const char* name, void * dest)
    int bmi_get_value_ptr(BMI_Model* model, const char* name, void ** ptr)
    int bmi_get_value_at_indices(BMI_Model* model, const char* name, void * dest, int *inds, int count)

    int bmi_set_value(BMI_Model* model, const char* name, void *src)
    int bmi_set_value_at_indices(BMI_Model* model, const char* name, int *inds, int count, void *src)

    int bmi_get_grid_rank(BMI_Model* model, int gid, int *rank)
    int bmi_get_grid_size(BMI_Model* model, int gid, int *size)
    int bmi_get_grid_type(BMI_Model* model, int gid, char *gtype)

    int bmi_get_grid_shape(BMI_Model* model, int gid, int* shape)
    int bmi_get_grid_spacing(BMI_Model* model, int gid, double* spacing)
    int bmi_get_grid_origin(BMI_Model* model, int gid, double* origin)

    int bmi_get_grid_x(BMI_Model *model, int grid, double *x)
    int bmi_get_grid_y(BMI_Model *model, int grid, double *y)
    int bmi_get_grid_z(BMI_Model *model, int grid, double *z)

    int bmi_get_grid_node_count(BMI_Model *model, int grid, int *count)
    int bmi_get_grid_edge_count(BMI_Model *model, int grid, int *count)
    int bmi_get_grid_face_count(BMI_Model *model, int grid, int *count)

    int bmi_get_grid_edge_nodes(BMI_Model *model, int grid, int *edge_nodes)
    int bmi_get_grid_face_edges(BMI_Model *model, int grid, int *face_edges)
    int bmi_get_grid_face_nodes(BMI_Model *model, int grid, int *face_nodes)
    int bmi_get_grid_nodes_per_face(BMI_Model *model, int grid, int *nodes_per_face)


def ok_or_raise(status):
    if status != 0:
        raise RuntimeError('error code {status}'.format(status=status))

{%- for entry_point in cookiecutter.entry_points.split(',') %}
    {% set pymt_class = entry_point.split('=')[0] %}
    {% set plugin_module, register_bmi = entry_point.split('=')[1].split(':') %}

# start: {{ pymt_class|lower }}.pyx

cdef extern from "bmi.h":
    BMI_Model* {{ register_bmi }}(BMI_Model *model)


cdef class {{ pymt_class }}:
    cdef BMI_Model* _bmi
    cdef char[2048] STR_BUFFER

    METADATA = "../data/{{ pymt_class }}"

    def __cinit__(self):
        # self._bmi = bmi_new()
        self._bmi = <BMI_Model*>malloc(sizeof(BMI_Model))

        if self._bmi is NULL:
            raise MemoryError()
        else:
            {{ register_bmi }}(self._bmi)

    def initialize(self, config_file):
        status = <int>bmi_initialize(self._bmi, <char*>config_file)
        # status = <int>bmi_initialize(self._bmi, <char*>config_file, <void**>&(self._bmi))
        ok_or_raise(status)

    def update(self):
        status = <int>bmi_update(self._bmi)
        ok_or_raise(status)

    def update_until(self, time):
        status = <int>bmi_update_until(self._bmi, time)
        ok_or_raise(status)

    # def update_frac(self, frac):
    #     status = <int>bmi_update_frac(self._bmi, frac)
    #     ok_or_raise(status)

    # def run_model(self):
    #     ok_or_raise(<int>bmi_run_model(self._bmi))

    def finalize(self):
        status = <int>bmi_finalize(self._bmi)
        ok_or_raise(status)

    cpdef object get_component_name(self):
        ok_or_raise(<int>bmi_get_component_name(self._bmi, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef int get_input_item_count(self):
        cdef int count = 0
        ok_or_raise(<int>bmi_get_input_item_count(self._bmi, &count))
        return count

    cpdef int get_output_item_count(self):
        cdef int count = 0
        ok_or_raise(<int>bmi_get_output_item_count(self._bmi, &count))
        return count

    def get_input_var_names(self):
        cdef list py_names = []
        cdef char** names
        cdef int i
        cdef int count
        cdef int status = 1

        ok_or_raise(<int>bmi_get_input_item_count(self._bmi, &count))

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * 2048 * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + 2048

            ok_or_raise(<int>bmi_get_input_var_names(self._bmi, names))

            for i in range(count):
                py_names.append(names[i])
        except Exception:
            raise
        finally:
            free(names[0])
            free(names)

        return tuple(py_names)

    def get_output_var_names(self):
        cdef list py_names = []
        cdef char** names
        cdef int i
        cdef int count
        cdef int status = 1

        ok_or_raise(<int>bmi_get_output_item_count(self._bmi, &count))

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * 2048 * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + 2048

            ok_or_raise(<int>bmi_get_output_var_names(self._bmi, names))

            for i in range(count):
                py_names.append(names[i])
        except Exception:
            raise
        finally:
            free(names[0])
            free(names)

        return tuple(py_names)

    cpdef int get_var_grid(self, name):
        cdef int gid
        ok_or_raise(<int>bmi_get_var_grid(self._bmi, <char*>name, &gid))
        return gid

    cpdef object get_var_type(self, name):
        ok_or_raise(<int>bmi_get_var_type(self._bmi, <char*>name, self.STR_BUFFER))
        return DTYPE_C_TO_PY[self.STR_BUFFER]

    cpdef object get_var_units(self, name):
        ok_or_raise(<int>bmi_get_var_units(self._bmi, <char*>name, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef int get_var_itemsize(self, name):
        cdef int itemsize
        ok_or_raise(<int>bmi_get_var_itemsize(self._bmi, <char*>name, &itemsize))
        return itemsize

    cpdef object get_var_location(self, name):
        ok_or_raise(<int>bmi_get_var_location(self._bmi, <char*>name, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef int get_var_nbytes(self, name):
        cdef int nbytes
        ok_or_raise(<int>bmi_get_var_nbytes(self._bmi, <char*>name, &nbytes))
        return nbytes

    cpdef double get_current_time(self):
        cdef double time
        ok_or_raise(<int>bmi_get_current_time(self._bmi, &time))
        return time

    cpdef double get_start_time(self):
        cdef double time
        ok_or_raise(<int>bmi_get_start_time(self._bmi, &time))
        return time

    cpdef double get_end_time(self):
        cdef double time
        ok_or_raise(<int>bmi_get_end_time(self._bmi, &time))
        return time

    cpdef object get_time_units(self):
        ok_or_raise(<int>bmi_get_time_units(self._bmi, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef double get_time_step(self):
        cdef double time
        ok_or_raise(<int>bmi_get_time_step(self._bmi, &time))
        return time

    cpdef get_value(self, name, np.ndarray buff):
        ok_or_raise(<int>bmi_get_value(self._bmi, <char*>name, buff.data))
        return buff

    cpdef get_value_ptr(self, name):
        cdef int status
        cdef int gid = self.get_var_grid(name)
        cdef int size = self.get_grid_size(gid)
        cdef void* ptr
        ok_or_raise(bmi_get_value_ptr(self._bmi, <char*>name, &ptr))
        return np.asarray(<np.float_t[:size]>ptr)

    cpdef set_value(self, name, np.ndarray buff):
        ok_or_raise(<int>bmi_set_value(self._bmi, <char*>name, buff.data))
        return buff

    cpdef int get_grid_rank(self, gid):
        cdef int rank
        ok_or_raise(<int>bmi_get_grid_rank(self._bmi, gid, &rank))
        return rank

    cpdef int get_grid_size(self, gid):
        cdef int size
        ok_or_raise(<int>bmi_get_grid_size(self._bmi, gid, &size))
        return size

    cpdef int get_grid_node_count(self, gid):
        cdef int size
        ok_or_raise(<int>bmi_get_grid_size(self._bmi, gid, &size))
        return size

    cpdef object get_grid_type(self, gid):
        ok_or_raise(bmi_get_grid_type(self._bmi, gid, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef get_grid_shape(self, int gid, np.ndarray[int, ndim=1] shape):
        ok_or_raise(<int>bmi_get_grid_shape(self._bmi, gid, &shape[0]))
        return shape

    cpdef get_grid_spacing(self, int gid, np.ndarray[double, ndim=1] spacing):
        ok_or_raise(<int>bmi_get_grid_spacing(self._bmi, gid, &spacing[0]))
        return spacing

    cpdef get_grid_origin(self, int gid, np.ndarray[double, ndim=1] origin):
        ok_or_raise(<int>bmi_get_grid_origin(self._bmi, gid, &origin[0]))
        return origin

{% endfor %}
