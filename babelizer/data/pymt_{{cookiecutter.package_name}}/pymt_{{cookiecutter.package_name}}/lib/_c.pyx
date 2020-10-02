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
    ctypedef struct Bmi:
        # pass
        int (*initialize)(void *self, const char *config_file)
        int (*update)(void *self);
        int (*update_until)(void *self, double then);
        int (*finalize)(void *self);

        # Exchange items
        int (*get_component_name)(void *self, char *name);
        int (*get_input_item_count)(void *self, int *count);
        int (*get_output_item_count)(void *self, int *count);
        int (*get_input_var_names)(void *self, char **names);
        int (*get_output_var_names)(void *self, char **names);

        # Variable information
        int (*get_var_grid)(void *self, const char *name, int *grid);
        int (*get_var_type)(void *self, const char *name, char *type);
        int (*get_var_units)(void *self, const char *name, char *units);
        int (*get_var_itemsize)(void *self, const char *name, int *size);
        int (*get_var_nbytes)(void *self, const char *name, int *nbytes);
        int (*get_var_location)(void *self, const char *name, char *location);

        # Time information
        int (*get_current_time)(void *self, double *time);
        int (*get_start_time)(void *self, double *time);
        int (*get_end_time)(void *self, double *time);
        int (*get_time_units)(void *self, char *units);
        int (*get_time_step)(void *self, double *time_step);

        # Getters
        int (*get_value)(void *self, const char *name, void *dest);
        int (*get_value_ptr)(void *self, const char *name, void **dest_ptr);
        int (*get_value_at_indices)(void *self, const char *name, void *dest, int *inds, int count);

        # Setters
        int (*set_value)(void *self, const char *name, void *src);
        int (*set_value_at_indices)(void *self, const char *name, int *inds, int count, void *src);

        # Grid information
        int (*get_grid_rank)(void *self, int grid, int *rank);
        int (*get_grid_size)(void *self, int grid, int *size);
        int (*get_grid_type)(void *self, int grid, char *type);

        # Uniform rectilinear
        int (*get_grid_shape)(void *self, int grid, int *shape);
        int (*get_grid_spacing)(void *self, int grid, double *spacing);
        int (*get_grid_origin)(void *self, int grid, double *origin);

        # Non-uniform rectilinear, curvilinear
        int (*get_grid_x)(void *self, int grid, double *x);
        int (*get_grid_y)(void *self, int grid, double *y);
        int (*get_grid_z)(void *self, int grid, double *z);

        # Unstructured
        int (*get_grid_node_count)(void *self, int grid, int *count);
        int (*get_grid_edge_count)(void *self, int grid, int *count);
        int (*get_grid_face_count)(void *self, int grid, int *count);
        int (*get_grid_edge_nodes)(void *self, int grid, int *edge_nodes);
        int (*get_grid_face_edges)(void *self, int grid, int *face_edges);
        int (*get_grid_face_nodes)(void *self, int grid, int *face_nodes);
        int (*get_grid_nodes_per_face)(void *self, int grid, int *nodes_per_face);


def ok_or_raise(status):
    if status != 0:
        raise RuntimeError('error code {status}'.format(status=status))

{%- for babelized_class, component in cookiecutter.components|dictsort %}
# start: {{ babelized_class|lower }}.pyx

cdef extern from "{{ component.header }}":
    Bmi* {{ component.class }}(Bmi *model)


cdef class {{ babelized_class }}:
    cdef Bmi* _bmi
    cdef char[2048] STR_BUFFER

    METADATA = "../data/{{ babelized_class }}"

    def __cinit__(self):
        self._bmi = <Bmi*>malloc(sizeof(Bmi))

        if self._bmi is NULL:
            raise MemoryError()
        else:
            {{ component.class }}(self._bmi)

    def __dealloc__(self):
        free(self._bmi)
        self._bmi = NULL

    def initialize(self, config_file):
        status = <int>self._bmi.initialize(self._bmi, <char*>config_file)
        ok_or_raise(status)

    def update(self):
        status = <int>self._bmi.update(self._bmi)
        ok_or_raise(status)

    def update_until(self, time):
        status = <int>self._bmi.update_until(self._bmi, time)
        ok_or_raise(status)

    def finalize(self):
        status = <int>self._bmi.finalize(self._bmi)
        ok_or_raise(status)

    cpdef object get_component_name(self):
        ok_or_raise(<int>self._bmi.get_component_name(self._bmi, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef int get_input_item_count(self):
        cdef int count = 0
        ok_or_raise(<int>self._bmi.get_input_item_count(self._bmi, &count))
        return count

    cpdef int get_output_item_count(self):
        cdef int count = 0
        ok_or_raise(<int>self._bmi.get_output_item_count(self._bmi, &count))
        return count

    def get_input_var_names(self):
        cdef list py_names = []
        cdef char** names
        cdef int i
        cdef int count
        cdef int status = 1

        ok_or_raise(<int>self._bmi.get_input_item_count(self._bmi, &count))

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * 2048 * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + 2048

            ok_or_raise(<int>self._bmi.get_input_var_names(self._bmi, names))

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

        ok_or_raise(<int>self._bmi.get_output_item_count(self._bmi, &count))

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * 2048 * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + 2048

            ok_or_raise(<int>self._bmi.get_output_var_names(self._bmi, names))

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
        ok_or_raise(<int>self._bmi.get_var_grid(self._bmi, <char*>name, &gid))
        return gid

    cpdef object get_var_type(self, name):
        ok_or_raise(<int>self._bmi.get_var_type(self._bmi, <char*>name, self.STR_BUFFER))
        return DTYPE_C_TO_PY[self.STR_BUFFER]

    cpdef object get_var_units(self, name):
        ok_or_raise(<int>self._bmi.get_var_units(self._bmi, <char*>name, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef int get_var_itemsize(self, name):
        cdef int itemsize
        ok_or_raise(<int>self._bmi.get_var_itemsize(self._bmi, <char*>name, &itemsize))
        return itemsize

    cpdef object get_var_location(self, name):
        ok_or_raise(<int>self._bmi.get_var_location(self._bmi, <char*>name, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef int get_var_nbytes(self, name):
        cdef int nbytes
        ok_or_raise(<int>self._bmi.get_var_nbytes(self._bmi, <char*>name, &nbytes))
        return nbytes

    cpdef double get_current_time(self):
        cdef double time
        ok_or_raise(<int>self._bmi.get_current_time(self._bmi, &time))
        return time

    cpdef double get_start_time(self):
        cdef double time
        ok_or_raise(<int>self._bmi.get_start_time(self._bmi, &time))
        return time

    cpdef double get_end_time(self):
        cdef double time
        ok_or_raise(<int>self._bmi.get_end_time(self._bmi, &time))
        return time

    cpdef object get_time_units(self):
        ok_or_raise(<int>self._bmi.get_time_units(self._bmi, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef double get_time_step(self):
        cdef double time
        ok_or_raise(<int>self._bmi.get_time_step(self._bmi, &time))
        return time

    cpdef get_value(self, name, np.ndarray buff):
        ok_or_raise(<int>self._bmi.get_value(self._bmi, <char*>name, buff.data))
        return buff

    cpdef get_value_ptr(self, name):
        cdef int status
        cdef int gid = self.get_var_grid(name)
        cdef int size = self.get_grid_size(gid)
        cdef void* ptr
        ok_or_raise(bmi_get_value_ptr(self._bmi, <char*>name, &ptr))
        return np.asarray(<np.float_t[:size]>ptr)

    cpdef set_value(self, name, np.ndarray buff):
        ok_or_raise(<int>self._bmi.set_value(self._bmi, <char*>name, buff.data))
        return buff

    cpdef int get_grid_rank(self, gid):
        cdef int rank
        ok_or_raise(<int>self._bmi.get_grid_rank(self._bmi, gid, &rank))
        return rank

    cpdef int get_grid_size(self, gid):
        cdef int size
        ok_or_raise(<int>self._bmi.get_grid_size(self._bmi, gid, &size))
        return size

    cpdef int get_grid_node_count(self, gid):
        cdef int size
        ok_or_raise(<int>self._bmi.get_grid_size(self._bmi, gid, &size))
        return size

    cpdef object get_grid_type(self, gid):
        ok_or_raise(bmi_get_grid_type(self._bmi, gid, self.STR_BUFFER))
        return self.STR_BUFFER

    cpdef get_grid_shape(self, int gid, np.ndarray[int, ndim=1] shape):
        ok_or_raise(<int>self._bmi.get_grid_shape(self._bmi, gid, &shape[0]))
        return shape

    cpdef get_grid_spacing(self, int gid, np.ndarray[double, ndim=1] spacing):
        ok_or_raise(<int>self._bmi.get_grid_spacing(self._bmi, gid, &spacing[0]))
        return spacing

    cpdef get_grid_origin(self, int gid, np.ndarray[double, ndim=1] origin):
        ok_or_raise(<int>self._bmi.get_grid_origin(self._bmi, gid, &origin[0]))
        return origin

{% endfor %}
