# cython: language_level=3
import ctypes
from libc.stdlib cimport malloc, free

cimport numpy as np
import numpy as np


SIZEOF_FLOAT = 8 * ctypes.sizeof(ctypes.c_float)
SIZEOF_DOUBLE = 8 * ctypes.sizeof(ctypes.c_double)
SIZEOF_INT = 8 * ctypes.sizeof(ctypes.c_int)

DTYPE_FLOAT = 'float{bits}'.format(bits=SIZEOF_FLOAT)
DTYPE_DOUBLE = 'float{bits}'.format(bits=SIZEOF_DOUBLE)
DTYPE_INT = 'int{bits}'.format(bits=SIZEOF_INT)

DTYPE_F_TO_PY = {
    'real': DTYPE_FLOAT,
    'real*4': DTYPE_FLOAT,
    'double precision': DTYPE_DOUBLE,
    'real*8': DTYPE_DOUBLE,
    'integer': DTYPE_INT,
}
for k in list(DTYPE_F_TO_PY.keys()):
    DTYPE_F_TO_PY[k.upper()] = DTYPE_F_TO_PY[k]

ENOMSG = 42  # No message of desired type

cdef extern from "bmi_interoperability.h":
    int MAX_COMPONENT_NAME
    int MAX_VAR_NAME
    int MAX_TYPE_NAME
    int MAX_UNITS_NAME

    int bmi_new()

    int bmi_initialize(int model, const char *config_file, int n_chars)
    int bmi_update(int model)
    int bmi_update_until(int model, double until)
    int bmi_finalize(int model)

    int bmi_get_component_name(int model, char *name, int n_chars)
    int bmi_get_input_item_count(int model, int *count)
    int bmi_get_output_item_count(int model, int *count)
    int bmi_get_input_var_names(int model, char **names, int n_names)
    int bmi_get_output_var_names(int model, char **names, int n_names)

    int bmi_get_start_time(int model, double *time)
    int bmi_get_end_time(int model, double *time)
    int bmi_get_current_time(int model, double *time)
    int bmi_get_time_step(int model, double *time)
    int bmi_get_time_units(int model, char *units, int n_chars)

    int bmi_get_var_grid(int model, const char *var_name, int n_chars,
                         int *grid_id)

    int bmi_get_grid_type(int model, int grid_id, char *type, int n_chars)
    int bmi_get_grid_rank(int model, int grid_id, int *rank)
    int bmi_get_grid_shape(int model, int grid_id, int *shape, int rank)
    int bmi_get_grid_size(int model, int grid_id, int *size)
    int bmi_get_grid_spacing(int model, int grid_id, double *spacing, int rank)
    int bmi_get_grid_origin(int model, int grid_id, double *origin, int rank)
    int bmi_get_grid_x(int model, int grid_id, double *x, int size)
    int bmi_get_grid_y(int model, int grid_id, double *y, int size)
    int bmi_get_grid_z(int model, int grid_id, double *z, int size)
    int bmi_get_grid_node_count(int model, int grid_id, int *count)
    int bmi_get_grid_edge_count(int model, int grid_id, int *count)
    int bmi_get_grid_face_count(int model, int grid_id, int *count)
    int bmi_get_grid_edge_nodes(int model, int grid_id,
                                int *edge_nodes, int size)
    int bmi_get_grid_face_edges(int model, int grid_id,
                                int *face_edges, int size)
    int bmi_get_grid_face_nodes(int model, int grid_id,
                                int *face_nodes, int size)
    int bmi_get_grid_nodes_per_face(int model, int grid_id,
                                    int *nodes_per_face, int size)

    int bmi_get_var_type(int model, const char *var_name, int n_chars,
                         char *type, int m_chars)
    int bmi_get_var_units(int model, const char *var_name, int n_chars,
                          char *units, int m_chars)
    int bmi_get_var_itemsize(int model, const char *var_name,
                             int n_chars, int *itemsize)
    int bmi_get_var_nbytes(int model, const char *var_name,
                           int n_chars, int *nbytes)
    int bmi_get_var_location(int model, const char *var_name, int n_chars,
                         char *location, int m_chars)

    int bmi_get_value_int(int model, const char *var_name, int n_chars,
                          void *buffer, int size)
    int bmi_get_value_float(int model, const char *var_name, int n_chars,
                            void *buffer, int size)
    int bmi_get_value_double(int model, const char *var_name, int n_chars,
                             void *buffer, int size)

    int bmi_get_value_ptr(int model, const char *var_name,
                          int n_chars, void **ptr)

    int bmi_set_value_int(int model, const char *var_name, int n_chars,
                          void *buffer, int size)
    int bmi_set_value_float(int model, const char *var_name, int n_chars,
                            void *buffer, int size)
    int bmi_set_value_double(int model, const char *var_name, int n_chars,
                             void *buffer, int size)


def ok_or_raise(status):
    if status != 0:
        raise RuntimeError('error code {status}'.format(status=status))


cpdef to_bytes(string):
    try:
        return bytes(string.encode('utf-8'))
    except AttributeError:
        return string


cpdef to_string(bytes):
    try:
        return bytes.decode('utf-8').rstrip()
    except AttributeError:
        return bytes

{%- for babelized_class in cookiecutter.components %}

# start: {{ babelized_class|lower }}.pyx

cdef class {{ babelized_class }}:

    cdef int _bmi
    cdef char[2048] STR_BUFFER

    METADATA = "../data/{{ babelized_class }}"

    def __cinit__(self):
        self._bmi = bmi_new()

        if self._bmi < 0:
            raise MemoryError('out of range model index: {}'
                              .format(self._bmi))

    cpdef int _get_model_index(self):
        return self._bmi

    cdef void reset_str_buffer(self):
        self.STR_BUFFER = np.zeros(MAX_VAR_NAME, dtype=np.byte)

    def initialize(self, config_file):
        status = <int>bmi_initialize(self._bmi, to_bytes(config_file),
                                     len(config_file))
        ok_or_raise(status)

    def finalize(self):
        status = <int>bmi_finalize(self._bmi)
        self._bmi = -1
        ok_or_raise(status)

    cpdef object get_component_name(self):
        self.reset_str_buffer()
        ok_or_raise(<int>bmi_get_component_name(self._bmi,
                                                self.STR_BUFFER,
                                                MAX_COMPONENT_NAME))
        return to_string(self.STR_BUFFER)

    cpdef int get_input_item_count(self):
        cdef int count = 0
        ok_or_raise(<int>bmi_get_input_item_count(self._bmi, &count))
        return count

    cpdef object get_input_var_names(self):
        cdef list py_names = []
        cdef char** names
        cdef int i
        cdef int count
        cdef int status = 1

        ok_or_raise(<int>bmi_get_input_item_count(self._bmi, &count))

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * MAX_VAR_NAME * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + MAX_VAR_NAME

            ok_or_raise(<int>bmi_get_input_var_names(self._bmi, names, count))

            for i in range(count):
                py_names.append(to_string(names[i]))

        except Exception:
            raise

        finally:
            free(names)

        return tuple(py_names)

    cpdef int get_output_item_count(self):
        cdef int count = 0
        ok_or_raise(<int>bmi_get_output_item_count(self._bmi, &count))
        return count

    cpdef object get_output_var_names(self):
        cdef list py_names = []
        cdef char** names
        cdef int i
        cdef int count
        cdef int status = 1

        ok_or_raise(<int>bmi_get_output_item_count(self._bmi, &count))

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * MAX_VAR_NAME * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + MAX_VAR_NAME

            ok_or_raise(<int>bmi_get_output_var_names(self._bmi, names, count))

            for i in range(count):
                py_names.append(to_string(names[i]))

        except Exception:
            raise

        finally:
            free(names)

        return tuple(py_names)

    cpdef double get_start_time(self):
        cdef double time
        ok_or_raise(<int>bmi_get_start_time(self._bmi, &time))
        return time

    cpdef double get_end_time(self):
        cdef double time
        ok_or_raise(<int>bmi_get_end_time(self._bmi, &time))
        return time

    cpdef double get_current_time(self):
        cdef double time
        ok_or_raise(<int>bmi_get_current_time(self._bmi, &time))
        return time

    cpdef double get_time_step(self):
        cdef double step
        ok_or_raise(<int>bmi_get_time_step(self._bmi, &step))
        return step

    cpdef object get_time_units(self):
        self.reset_str_buffer()
        ok_or_raise(<int>bmi_get_time_units(self._bmi, self.STR_BUFFER,
                                            MAX_UNITS_NAME))
        return to_string(self.STR_BUFFER)

    cpdef update(self):
        status = <int>bmi_update(self._bmi)
        ok_or_raise(status)

    cpdef update_until(self, time_later):
        status = <int>bmi_update_until(self._bmi, time_later)
        ok_or_raise(status)

    cpdef int get_var_grid(self, var_name):
        cdef int grid_id
        ok_or_raise(<int>bmi_get_var_grid(self._bmi,
                                          to_bytes(var_name),
                                          len(var_name), &grid_id))
        return grid_id

    cpdef object get_grid_type(self, grid_id):
        self.reset_str_buffer()
        ok_or_raise(<int>bmi_get_grid_type(self._bmi, grid_id,
                                           self.STR_BUFFER,
                                           MAX_TYPE_NAME))
        return to_string(self.STR_BUFFER)

    cpdef int get_grid_rank(self, grid_id):
        cdef int rank
        ok_or_raise(<int>bmi_get_grid_rank(self._bmi, grid_id, &rank))
        return rank

    cpdef int get_grid_size(self, grid_id):
        cdef int size
        ok_or_raise(<int>bmi_get_grid_size(self._bmi, grid_id, &size))
        return size

    cpdef np.ndarray get_grid_shape(self, grid_id, \
                                    np.ndarray[int, ndim=1] shape):
        cdef int rank = self.get_grid_rank(grid_id)
        if rank > 0:
            ok_or_raise(<int>bmi_get_grid_shape(self._bmi, grid_id,
                                                &shape[0], rank))
        return shape

    cpdef np.ndarray get_grid_spacing(self, grid_id, \
                                      np.ndarray[double, ndim=1] spacing):
        cdef int rank = self.get_grid_rank(grid_id)
        if rank > 0:
            ok_or_raise(<int>bmi_get_grid_spacing(self._bmi, grid_id,
                                                  &spacing[0], rank))
        return spacing

    cpdef np.ndarray get_grid_origin(self, grid_id, \
                                     np.ndarray[double, ndim=1] origin):
        cdef int rank = self.get_grid_rank(grid_id)
        if rank > 0:
            ok_or_raise(<int>bmi_get_grid_origin(self._bmi, grid_id,
                                                 &origin[0], rank))
        return origin

    cpdef np.ndarray get_grid_x(self, grid_id, \
                                np.ndarray[double, ndim=1] grid_x):
        cdef int size

        if self.get_grid_type(grid_id) == 'rectilinear':
            rank = self.get_grid_rank(grid_id)
            shape = np.ndarray(rank, dtype=np.int32)
            size = self.get_grid_shape(grid_id, shape)[1]
        else:
            size = self.get_grid_size(grid_id)

        ok_or_raise(<int>bmi_get_grid_x(self._bmi, grid_id,
                                        &grid_x[0], size))
        return grid_x

    cpdef np.ndarray get_grid_y(self, grid_id, \
                                np.ndarray[double, ndim=1] grid_y):
        cdef int size

        if self.get_grid_type(grid_id) == 'rectilinear':
            rank = self.get_grid_rank(grid_id)
            shape = np.ndarray(rank, dtype=np.int32)
            size = self.get_grid_shape(grid_id, shape)[0]
        else:
            size = self.get_grid_size(grid_id)

        ok_or_raise(<int>bmi_get_grid_y(self._bmi, grid_id,
                                        &grid_y[0], size))
        return grid_y

    cpdef np.ndarray get_grid_z(self, grid_id, \
                                np.ndarray[double, ndim=1] grid_z):
        cdef int size

        if self.get_grid_type(grid_id) == 'rectilinear':
            rank = self.get_grid_rank(grid_id)
            shape = np.ndarray(rank, dtype=np.int32)
            self.get_grid_shape(grid_id, shape)
            if rank > 2:
                size = shape[2]
            else:
                size = 1
        else:
            size = self.get_grid_size(grid_id)

        ok_or_raise(<int>bmi_get_grid_z(self._bmi, grid_id,
                                        &grid_z[0], size))
        return grid_z

    cpdef int get_grid_node_count(self, grid_id):
        cdef int node_count
        ok_or_raise(<int>bmi_get_grid_node_count(self._bmi, grid_id,
                                                 &node_count))
        return node_count

    cpdef int get_grid_edge_count(self, grid_id):
        cdef int edge_count
        ok_or_raise(<int>bmi_get_grid_edge_count(self._bmi, grid_id,
                                                 &edge_count))
        return edge_count

    cpdef int get_grid_face_count(self, grid_id):
        cdef int face_count
        ok_or_raise(<int>bmi_get_grid_face_count(self._bmi, grid_id,
                                                 &face_count))
        return face_count

    cpdef np.ndarray get_grid_edge_nodes(self, grid_id, \
                                         np.ndarray[int, ndim=1] edge_nodes):
        cdef int size = len(edge_nodes)
        if size > 0:
            ok_or_raise(<int>bmi_get_grid_edge_nodes(self._bmi, grid_id,
                                                     &edge_nodes[0], size))
        return edge_nodes

    cpdef np.ndarray get_grid_face_edges(self, grid_id, \
                                         np.ndarray[int, ndim=1] face_edges):
        cdef int size = len(face_edges)
        if size > 0:
            ok_or_raise(<int>bmi_get_grid_face_edges(self._bmi, grid_id,
                                                     &face_edges[0], size))
        return face_edges

    cpdef np.ndarray get_grid_face_nodes(self, grid_id, \
                                         np.ndarray[int, ndim=1] face_nodes):
        cdef int size = len(face_nodes)
        if size > 0:
            ok_or_raise(<int>bmi_get_grid_face_nodes(self._bmi, grid_id,
                                                     &face_nodes[0], size))
        return face_nodes

    cpdef np.ndarray get_grid_nodes_per_face(self, grid_id, \
                                         np.ndarray[int, ndim=1] nodes_per_face):
        cdef int size = self.get_grid_face_count(grid_id)
        if size > 0:
            ok_or_raise(<int>bmi_get_grid_nodes_per_face(self._bmi, grid_id,
                                                         &nodes_per_face[0], size))
        return nodes_per_face

    cpdef object get_var_type(self, var_name):
        self.reset_str_buffer()
        ok_or_raise(<int>bmi_get_var_type(self._bmi,
                                          to_bytes(var_name),
                                          len(var_name),
                                          self.STR_BUFFER,
                                          MAX_TYPE_NAME))
        return DTYPE_F_TO_PY[to_string(self.STR_BUFFER)]

    cpdef object get_var_units(self, var_name):
        self.reset_str_buffer()
        ok_or_raise(<int>bmi_get_var_units(self._bmi,
                                           to_bytes(var_name),
                                           len(var_name),
                                           self.STR_BUFFER,
                                           MAX_UNITS_NAME))
        return to_string(self.STR_BUFFER)

    cpdef int get_var_itemsize(self, var_name):
        cdef int itemsize
        ok_or_raise(<int>bmi_get_var_itemsize(self._bmi,
                                              to_bytes(var_name),
                                              len(var_name), &itemsize))
        return itemsize

    cpdef int get_var_nbytes(self, var_name):
        cdef int nbytes
        ok_or_raise(<int>bmi_get_var_nbytes(self._bmi,
                                            to_bytes(var_name),
                                            len(var_name), &nbytes))
        return nbytes

    cpdef object get_var_location(self, var_name):
        self.reset_str_buffer()
        ok_or_raise(<int>bmi_get_var_location(self._bmi,
                                              to_bytes(var_name),
                                              len(var_name),
                                              self.STR_BUFFER,
                                              MAX_TYPE_NAME))
        return to_string(self.STR_BUFFER)

    cpdef np.ndarray get_value(self, var_name, np.ndarray buffer):
        cdef int grid_id = self.get_var_grid(var_name)
        cdef int grid_size = self.get_grid_size(grid_id)
        type = self.get_var_type(var_name)

        if type == DTYPE_DOUBLE:
            ok_or_raise(<int>bmi_get_value_double(self._bmi,
                                                  to_bytes(var_name),
                                                  len(var_name),
                                                  buffer.data,
                                                  grid_size))
        elif type == DTYPE_INT:
            ok_or_raise(<int>bmi_get_value_int(self._bmi,
                                               to_bytes(var_name),
                                               len(var_name),
                                               buffer.data,
                                               grid_size))
        elif type == DTYPE_FLOAT:
            ok_or_raise(<int>bmi_get_value_float(self._bmi,
                                                 to_bytes(var_name),
                                                 len(var_name),
                                                 buffer.data,
                                                 grid_size))
        else:
            ok_or_raise(ENOMSG)

        return buffer

    cpdef np.ndarray get_value_ptr(self, var_name):
        cdef int grid_id = self.get_var_grid(var_name)
        cdef int grid_size = self.get_grid_size(grid_id)
        cdef void* ptr
        type = self.get_var_type(var_name)

        ok_or_raise(<int>bmi_get_value_ptr(self._bmi,
                                           to_bytes(var_name),
                                           len(var_name), &ptr))

        if type == DTYPE_DOUBLE:
            return np.asarray(<np.float64_t[:grid_size]>ptr)
        elif type == DTYPE_INT:
            return np.asarray(<np.int32_t[:grid_size]>ptr)
        elif type == DTYPE_FLOAT:
            return np.asarray(<np.float32_t[:grid_size]>ptr)
        else:
            return ok_or_raise(ENOMSG)

    cpdef set_value(self, var_name, np.ndarray buffer):
        cdef int grid_id = self.get_var_grid(var_name)
        cdef int grid_size = self.get_grid_size(grid_id)
        type = self.get_var_type(var_name)

        if type == DTYPE_DOUBLE:
            ok_or_raise(<int>bmi_set_value_double(self._bmi,
                                                  to_bytes(var_name),
                                                  len(var_name),
                                                  buffer.data,
                                                  grid_size))
        elif type == DTYPE_INT:
            ok_or_raise(<int>bmi_set_value_int(self._bmi,
                                               to_bytes(var_name),
                                               len(var_name),
                                               buffer.data,
                                               grid_size))
        elif type == DTYPE_FLOAT:
            ok_or_raise(<int>bmi_set_value_float(self._bmi,
                                                 to_bytes(var_name),
                                                 len(var_name),
                                                 buffer.data,
                                                 grid_size))
        else:
            ok_or_raise(ENOMSG)

        return buffer
{%- endfor %}
