import ctypes
from libc.stdlib cimport malloc, free

cimport numpy as np
import numpy as np


SIZEOF_FLOAT = 8 * ctypes.sizeof(ctypes.c_float)
SIZEOF_DOUBLE = 8 * ctypes.sizeof(ctypes.c_double)
SIZEOF_INT = 8 * ctypes.sizeof(ctypes.c_int)

DTYPE_F_TO_PY = {
    'real': 'float{bits}'.format(bits=SIZEOF_FLOAT),
    'real*4': 'float{bits}'.format(bits=SIZEOF_FLOAT),
    'double precision': 'float{bits}'.format(bits=SIZEOF_DOUBLE),
    'real*8': 'float{bits}'.format(bits=SIZEOF_DOUBLE),
    'integer': 'int{bits}'.format(bits=SIZEOF_INT),
}


cdef extern from "bmi_interoperability.h":
    int MAX_COMPONENT_NAME
    int MAX_VAR_NAME
    int MAX_TYPE_NAME
    int MAX_UNITS_NAME

    int bmi_new()

    int bmi_initialize(int model, const char *config_file, int n_chars)
    int bmi_update(int model)
    int bmi_update_until(int model, double until)
    int bmi_update_frac(int model, double frac)
    int bmi_finalize(int model)

    int bmi_get_component_name(int model, char *name, int n_chars)
    int bmi_get_input_var_name_count(int model, int *count)
    int bmi_get_output_var_name_count(int model, int *count)
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
    int bmi_get_grid_spacing(int model, int grid_id, float *spacing, int rank)
    int bmi_get_grid_origin(int model, int grid_id, float *origin, int rank)
    int bmi_get_grid_x(int model, int grid_id, float *x, int size)
    int bmi_get_grid_y(int model, int grid_id, float *y, int size)
    int bmi_get_grid_z(int model, int grid_id, float *z, int size)
    int bmi_get_grid_connectivity(int model, int grid_id, int *conn, int size)
    int bmi_get_grid_offset(int model, int grid_id, int *offset, int size)

    int bmi_get_var_type(int model, const char *var_name, int n_chars,
                         char *type, int m_chars)
    int bmi_get_var_units(int model, const char *var_name, int n_chars,
                          char *units, int m_chars)
    int bmi_get_var_itemsize(int model, const char *var_name,
                             int n_chars, int *itemsize)
    int bmi_get_var_nbytes(int model, const char *var_name,
                           int n_chars, int *nbytes)

    int bmi_get_value_int(int model, const char *var_name, int n_chars,
                          void *buffer, int size)
    int bmi_get_value_float(int model, const char *var_name, int n_chars,
                            void *buffer, int size)
    int bmi_get_value_double(int model, const char *var_name, int n_chars,
                             void *buffer, int size)

    int bmi_get_value_ref(int model, const char *var_name,
                          int n_chars, void **ref)

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

{%- set entry_point = cookiecutter.entry_points.split(',')[0] -%}
{% set pymt_class = entry_point.split('=')[0] %}
{% set plugin_module, plugin_class = entry_point.split('=')[1].split(':') %}

# start: {{ pymt_class|lower }}.pyx

cdef class {{ pymt_class }}:

    cdef int _bmi
    cdef char[2048] STR_BUFFER

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

    cpdef int get_input_var_name_count(self):
        cdef int count = 0
        ok_or_raise(<int>bmi_get_input_var_name_count(self._bmi, &count))
        return count

    cpdef object get_input_var_names(self):
        cdef list py_names = []
        cdef char** names
        cdef int i
        cdef int count
        cdef int status = 1

        ok_or_raise(<int>bmi_get_input_var_name_count(self._bmi, &count))

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

    cpdef int get_output_var_name_count(self):
        cdef int count = 0
        ok_or_raise(<int>bmi_get_output_var_name_count(self._bmi, &count))
        return count

    cpdef object get_output_var_names(self):
        cdef list py_names = []
        cdef char** names
        cdef int i
        cdef int count
        cdef int status = 1

        ok_or_raise(<int>bmi_get_output_var_name_count(self._bmi, &count))

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

    cpdef update_frac(self, time_frac):
        status = <int>bmi_update_frac(self._bmi, time_frac)
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
        ok_or_raise(<int>bmi_get_grid_shape(self._bmi, grid_id,
                                            &shape[0], rank))
        return shape

    cpdef np.ndarray get_grid_spacing(self, grid_id, \
                                      np.ndarray[float, ndim=1] spacing):
        cdef int rank = self.get_grid_rank(grid_id)
        ok_or_raise(<int>bmi_get_grid_spacing(self._bmi, grid_id,
                                              &spacing[0], rank))
        return spacing

    cpdef np.ndarray get_grid_origin(self, grid_id, \
                                     np.ndarray[float, ndim=1] origin):
        cdef int rank = self.get_grid_rank(grid_id)
        ok_or_raise(<int>bmi_get_grid_origin(self._bmi, grid_id,
                                             &origin[0], rank))
        return origin

    cpdef np.ndarray get_grid_x(self, grid_id, \
                                np.ndarray[float, ndim=1] grid_x):
        cdef int size = self.get_grid_size(grid_id)
        ok_or_raise(<int>bmi_get_grid_x(self._bmi, grid_id,
                                        &grid_x[0], size))
        return grid_x

    cpdef np.ndarray get_grid_y(self, grid_id, \
                                np.ndarray[float, ndim=1] grid_y):
        cdef int size = self.get_grid_size(grid_id)
        ok_or_raise(<int>bmi_get_grid_y(self._bmi, grid_id,
                                        &grid_y[0], size))
        return grid_y

    cpdef np.ndarray get_grid_z(self, grid_id, \
                                np.ndarray[float, ndim=1] grid_z):
        cdef int size = self.get_grid_size(grid_id)
        ok_or_raise(<int>bmi_get_grid_z(self._bmi, grid_id,
                                        &grid_z[0], size))
        return grid_z

    cpdef np.ndarray get_grid_connectivity(self, grid_id, \
                                           np.ndarray[int, ndim=1] conn):
        cdef int size = self.get_grid_size(grid_id)
        ok_or_raise(<int>bmi_get_grid_connectivity(self._bmi, grid_id,
                                                   &conn[0], size))
        return conn

    cpdef np.ndarray get_grid_offset(self, grid_id, 
                                     np.ndarray[int, ndim=1] offset):
        cdef int size = self.get_grid_size(grid_id)
        ok_or_raise(<int>bmi_get_grid_offset(self._bmi, grid_id,
                                             &offset[0], size))
        return offset

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

    cpdef np.ndarray get_value(self, var_name, np.ndarray buffer):
        cdef int grid_id = self.get_var_grid(var_name)
        cdef int grid_size = self.get_grid_size(grid_id)
        type = self.get_var_type(var_name)

        if type.startswith('double'):
            ok_or_raise(<int>bmi_get_value_double(self._bmi,
                                                  to_bytes(var_name),
                                                  len(var_name),
                                                  buffer.data,
                                                  grid_size))
        elif type.startswith('int'):
            ok_or_raise(<int>bmi_get_value_int(self._bmi,
                                               to_bytes(var_name),
                                               len(var_name),
                                               buffer.data,
                                               grid_size))
        else:
            ok_or_raise(<int>bmi_get_value_float(self._bmi,
                                                 to_bytes(var_name),
                                                 len(var_name),
                                                 buffer.data,
                                                 grid_size))

        return buffer

    cpdef np.ndarray get_value_ref(self, var_name):
        cdef int grid_id = self.get_var_grid(var_name)
        cdef int grid_size = self.get_grid_size(grid_id)
        cdef void* ptr
        type = self.get_var_type(var_name)

        ok_or_raise(<int>bmi_get_value_ref(self._bmi,
                                           to_bytes(var_name),
                                           len(var_name), &ptr))

        if type.startswith('double'):
            return np.asarray(<np.float64_t[:grid_size]>ptr)
        elif type.startswith('int'):
            return np.asarray(<np.int32_t[:grid_size]>ptr)
        else:
            return np.asarray(<np.float32_t[:grid_size]>ptr)

    cpdef set_value(self, var_name, np.ndarray buffer):
        cdef int grid_id = self.get_var_grid(var_name)
        cdef int grid_size = self.get_grid_size(grid_id)
        type = self.get_var_type(var_name)

        if type.startswith('double'):
            ok_or_raise(<int>bmi_set_value_double(self._bmi,
                                                  to_bytes(var_name),
                                                  len(var_name),
                                                  buffer.data,
                                                  grid_size))
        elif type.startswith('int'):
            ok_or_raise(<int>bmi_set_value_int(self._bmi,
                                               to_bytes(var_name),
                                               len(var_name),
                                               buffer.data,
                                               grid_size))
        else:
            ok_or_raise(<int>bmi_set_value_float(self._bmi,
                                                 to_bytes(var_name),
                                                 len(var_name),
                                                 buffer.data,
                                                 grid_size))
        return buffer
