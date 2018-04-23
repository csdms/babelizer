import ctypes
from libc.stdlib cimport malloc, free

cimport numpy as np
import numpy as np

cimport _{{cookiecutter.module_name}}


{% if cookiecutter.language == 'c' %}

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


cdef extern from "bmi.c":
    BMI_Model* bmi_new()

    int bmi_initialize(BMI_Model* model, const char *config_file, void**self)
    int bmi_update(BMI_Model* model)
    int bmi_update_until(BMI_Model* model, double until)
    int bmi_update_frac(BMI_Model* model, double frac)
    int bmi_finalize(BMI_Model* model)
    int bmi_run_model(BMI_Model* model)

    int bmi_get_component_name(BMI_Model* model, char* name)
    int bmi_get_input_var_name_count(BMI_Model* model, int *count)
    int bmi_get_output_var_name_count(BMI_Model* model, int *count)

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

    int bmi_get_value(BMI_Model* model, const char* name, void * buffer)
    int bmi_get_value_ptr(BMI_Model* model, const char* name, void ** ptr)

    int bmi_set_value(BMI_Model* model, const char* name, void *buffer)

    int bmi_get_grid_rank(BMI_Model* model, int gid, int *rank)
    int bmi_get_grid_size(BMI_Model* model, int gid, int *size)
    int bmi_get_grid_type(BMI_Model* model, int gid, char *gtype)

    int bmi_get_grid_shape(BMI_Model* model, int gid, int* shape)
    int bmi_get_grid_spacing(BMI_Model* model, int gid, double* spacing)
    int bmi_get_grid_origin(BMI_Model* model, int gid, double* origin)


def ok_or_raise(status):
    if status != 0:
        raise RuntimeError('error code {status}'.format(status=status))


cdef class {{cookiecutter.class_name}}:
    cdef _{{cookiecutter.module_name}}.BMI_Model* _bmi
    cdef char[2048] STR_BUFFER

    def __cinit__(self):
        self._bmi = bmi_new()

        if self._bmi is NULL:
            raise MemoryError()
        else:
            {{cookiecutter.bmi_register}}(self._bmi)

    def initialize(self, config_file):
        status = <int>bmi_initialize(self._bmi, config_file, <void**>&(self._bmi))
        ok_or_raise(status)
        # return <int>bmi_initialize(self._bmi, config_file, <void**>&(self._bmi)), None

    def update(self):
        status = <int>bmi_update(self._bmi)
        ok_or_raise(status)
        # return <int>bmi_update(self._bmi), None

    def update_until(self, time):
        status = <int>bmi_update_until(self._bmi, time)
        ok_or_raise(status)
        # return <int>bmi_update_until(self._bmi, time), None

    def update_frac(self, frac):
        ok_or_raise(<int>bmi_update_frac(self._bmi, frac))
        return <int>bmi_update_frac(self._bmi, frac), None

    def run_model(self):
        ok_or_raise(<int>bmi_run_model(self._bmi))
        # return <int>bmi_run_model(self._bmi), None

    def finalize(self):
        ok_or_raise(<int>bmi_finalize(self._bmi))
        return <int>bmi_finalize(self._bmi), None

    cpdef bytes get_component_name(self):
        ok_or_raise(<int>bmi_get_component_name(self._bmi, self.STR_BUFFER))
        return <bytes>self.STR_BUFFER
        # return <int>bmi_get_component_name(self._bmi, self.STR_BUFFER), <bytes>self.STR_BUFFER

    cpdef int get_input_var_name_count(self):
        cdef int count = 0
        ok_or_raise(<int>bmi_get_input_var_name_count(self._bmi, &count))
        return count
        # return <int>bmi_get_input_var_name_count(self._bmi, &count), count

    cpdef int get_output_var_name_count(self):
        cdef int count = 0
        ok_or_raise(<int>bmi_get_output_var_name_count(self._bmi, &count))
        return count
        # return <int>bmi_get_output_var_name_count(self._bmi, &count), count

    def get_input_var_names(self):
        cdef list py_names = []
        cdef char** names
        cdef int i
        cdef int count
        cdef int status = 1

        ok_or_raise(<int>bmi_get_input_var_name_count(self._bmi, &count))

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * 2048 * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + 2048

            # status = bmi_get_input_var_names(self._bmi, names)
            ok_or_raise(<int>bmi_get_input_var_names(self._bmi, names))

            for i in range(count):
                py_names.append(<bytes>(names[i]))
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

        ok_or_raise(<int>bmi_get_output_var_name_count(self._bmi, &count))

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * 2048 * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + 2048

            ok_or_raise(<int>bmi_get_output_var_names(self._bmi, names))

            for i in range(count):
                py_names.append(<bytes>(names[i]))
        except Exception:
            raise
        finally:
            free(names[0])
            free(names)

        return tuple(py_names)

    cpdef int get_var_grid(self, name):
        cdef int gid
        ok_or_raise(<int>bmi_get_var_grid(self._bmi, name, &gid))
        return gid
        # return <int>bmi_get_var_grid(self._bmi, name, &gid), gid

    cpdef bytes get_var_type(self, name):
        ok_or_raise(<int>bmi_get_var_type(self._bmi, name, self.STR_BUFFER))
        return DTYPE_C_TO_PY[<bytes>self.STR_BUFFER]
        # return <int>bmi_get_var_type(self._bmi, name, self.STR_BUFFER), DTYPE_C_TO_PY[<bytes>self.STR_BUFFER]

    cpdef bytes get_var_units(self, name):
        ok_or_raise(<int>bmi_get_var_units(self._bmi, name, self.STR_BUFFER))
        return <bytes>self.STR_BUFFER
        # return <int>bmi_get_var_units(self._bmi, name, self.STR_BUFFER), <bytes>self.STR_BUFFER

    cpdef int get_var_itemsize(self, name):
        cdef int itemsize
        ok_or_raise(<int>bmi_get_var_itemsize(self._bmi, name, &itemsize))
        return itemsize
        # return <int>bmi_get_var_itemsize(self._bmi, name, &itemsize), itemsize

    cpdef bytes get_var_location(self, name):
        ok_or_raise(<int>bmi_get_var_location(self._bmi, name, self.STR_BUFFER))
        return <bytes>self.STR_BUFFER
        # return <int>bmi_get_var_location(self._bmi, name, self.STR_BUFFER), <bytes>self.STR_BUFFER

    cpdef int get_var_nbytes(self, name):
        cdef int nbytes
        ok_or_raise(<int>bmi_get_var_nbytes(self._bmi, name, &nbytes))
        return nbytes
        # return <int>bmi_get_var_nbytes(self._bmi, name, &nbytes), nbytes

    cpdef double get_current_time(self):
        cdef double time
        ok_or_raise(<int>bmi_get_current_time(self._bmi, &time))
        return time
        # return <int>bmi_get_current_time(self._bmi, &time), time

    cpdef double get_start_time(self):
        cdef double time
        ok_or_raise(<int>bmi_get_start_time(self._bmi, &time))
        return time
        # return <int>bmi_get_start_time(self._bmi, &time), time

    cpdef double get_end_time(self):
        cdef double time
        ok_or_raise(<int>bmi_get_end_time(self._bmi, &time))
        return time
        # return <int>bmi_get_end_time(self._bmi, &time), time

    cpdef bytes get_time_units(self):
        ok_or_raise(<int>bmi_get_time_units(self._bmi, self.STR_BUFFER))
        return <bytes>self.STR_BUFFER
        # return <int>bmi_get_time_units(self._bmi, self.STR_BUFFER), <bytes>self.STR_BUFFER

    cpdef double get_time_step(self):
        cdef double time
        ok_or_raise(<int>bmi_get_time_step(self._bmi, &time))
        return time
        # return <int>bmi_get_time_step(self._bmi, &time), time

    cpdef get_value(self, name, np.ndarray buff):
        # return <int>bmi_get_value(self._bmi, <char*>name, &buff.data[0]), buff
        ok_or_raise(<int>bmi_get_value(self._bmi, <char*>name, buff.data))
        return buff
        # return <int>bmi_get_value(self._bmi, <char*>name, buff.data), buff

    cpdef get_value_ptr(self, name):
        cdef int status
        cdef int gid = self.get_var_grid(name)
        cdef int size = self.get_grid_size(gid)
        cdef void* ptr
        ok_or_raise(bmi_get_value_ptr(self._bmi, name, &ptr))
        return np.asarray(<np.float_t[:size]>ptr)

    cpdef set_value(self, name, np.ndarray buff):
        ok_or_raise(<int>bmi_set_value(self._bmi, name, buff.data))
        return buff
        # return <int>bmi_set_value(self._bmi, name, buff.data), buff

    cpdef int get_grid_rank(self, gid):
        cdef int rank
        ok_or_raise(<int>bmi_get_grid_rank(self._bmi, gid, &rank))
        return rank
        # return <int>bmi_get_grid_rank(self._bmi, gid, &rank), rank

    cpdef int get_grid_size(self, gid):
        cdef int size
        ok_or_raise(<int>bmi_get_grid_size(self._bmi, gid, &size))
        return size
        # return <int>bmi_get_grid_size(self._bmi, gid, &size), size

    cpdef bytes get_grid_type(self, gid):
        ok_or_raise(bmi_get_grid_type(self._bmi, gid, self.STR_BUFFER))
        # cdef int status = bmi_get_grid_type(self._bmi, gid, self.STR_BUFFER)
        return <bytes>self.STR_BUFFER

    cpdef get_grid_shape(self, int gid, np.ndarray[int, ndim=1] shape):
        ok_or_raise(<int>bmi_get_grid_shape(self._bmi, gid, &shape[0]))
        return shape
        # return <int>bmi_get_grid_shape(self._bmi, gid, &shape[0]), shape

    cpdef get_grid_spacing(self, int gid, np.ndarray[double, ndim=1] spacing):
        ok_or_raise(<int>bmi_get_grid_spacing(self._bmi, gid, &spacing[0]))
        return spacing
        # return <int>bmi_get_grid_spacing(self._bmi, gid, &spacing[0]), spacing

    cpdef get_grid_origin(self, int gid, np.ndarray[double, ndim=1] origin):
        ok_or_raise(<int>bmi_get_grid_origin(self._bmi, gid, &origin[0]))
        return origin
        # return <int>bmi_get_grid_origin(self._bmi, gid, &origin[0]), origin

{% elif cookiecutter.language == 'c++' %}

cdef class {{cookiecutter.class_name}}:
    cdef _{{cookiecutter.module_name}}.Model _bmi
    cdef char[2048] STR_BUFFER

    def __cinit__(self):
        pass

    def buffer(self):
        return <bytes>self.STR_BUFFER

    def initialize(self, config_file):
        self._bmi.Initialize(config_file)

    def update(self):
        self._bmi.Update()

    def finalize(self):
        self._bmi.Finalize()

    cpdef int get_var_grid(self, name):
        return self._bmi.GetVarGrid(name)

    cpdef bytes get_var_type(self, name):
        self._bmi.GetVarType(name, self.STR_BUFFER)
        return self.STR_BUFFER

    cpdef bytes get_var_units(self, name):
        self._bmi.GetVarUnits(name, self.STR_BUFFER)
        return self.STR_BUFFER

    cpdef int get_var_itemsize(self, name):
        return self._bmi.GetVarItemsize(name)

    cpdef int get_var_nbytes(self, name):
        return self._bmi.GetVarNbytes(name)

    cpdef bytes get_var_location(self, name):
        self._bmi.GetVarLocation(name, self.STR_BUFFER)
        return self.STR_BUFFER

    cpdef get_component_name(self):
        self._bmi.GetComponentName(self.STR_BUFFER)
        return <bytes>self.STR_BUFFER

    cpdef int get_input_var_name_count(self):
        return self._bmi.GetInputVarNameCount()

    cpdef int get_output_var_name_count(self):
        return self._bmi.GetOutputVarNameCount()

    def get_input_var_names(self):
        cdef list py_names = []
        cdef char** names
        cdef int i
        cdef int count = self._bmi.GetInputVarNameCount()

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * 2048 * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + 2048
            self._bmi.GetInputVarNames(names)

            for i in range(count):
                py_names.append(<bytes>(names[i]))
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
        cdef int count = self._bmi.GetOutputVarNameCount()

        try:
            names = <char**>malloc(count * sizeof(char*))
            names[0] = <char*>malloc(count * 2048 * sizeof(char))
            for i in range(1, count):
                names[i] = names[i - 1] + 2048
            self._bmi.GetOutputVarNames(names)

            for i in range(count):
                py_names.append(<bytes>(names[i]))
        except Exception:
            raise
        finally:
            free(names[0])
            free(names)

        return tuple(py_names)

    cpdef double get_current_time(self):
        return self._bmi.GetCurrentTime()

    cpdef double get_start_time(self):
        return self._bmi.GetStartTime()

    cpdef double get_end_time(self):
        return self._bmi.GetEndTime()

    cpdef bytes get_time_units(self):
        self._bmi.GetTimeUnits(self.STR_BUFFER)
        return <bytes>self.STR_BUFFER

    cpdef double get_time_step(self):
        return self._bmi.GetTimeStep()

    cpdef get_value(self, name, np.ndarray buff):
        self._bmi.GetValue(name, buff.data)
        return buff

    cpdef set_value(self, name, np.ndarray buff):
        self._bmi.SetValue(name, buff.data)
        return buff

    cpdef int get_grid_rank(self, gid):
        return self._bmi.GetGridRank(gid)

    cpdef int get_grid_size(self, gid):
        return self._bmi.GetGridSize(gid)

    cpdef int get_grid_number_of_nodes(self, gid):
        return self._bmi.GetGridSize(gid)

    cpdef int get_grid_number_of_faces(self, gid):
        return self._bmi.GetGridNumberOfFaces(gid)

    # cpdef int get_grid_number_of_edges(self, gid):
    #     return self._bmi.GetGridNumberOfEdges(gid)

    cpdef bytes get_grid_type(self, gid):
        self._bmi.GetGridType(gid, self.STR_BUFFER)
        return <bytes>self.STR_BUFFER

    cpdef get_grid_x(self, gid, np.ndarray[double, ndim=1] buff):
        self._bmi.GetGridX(gid, &buff[0])
        return buff

    cpdef get_grid_y(self, gid, np.ndarray[double, ndim=1] buff):
        self._bmi.GetGridY(gid, &buff[0])
        return buff

    cpdef get_grid_face_nodes(self, gid, np.ndarray[int, ndim=1] buff):
        self._bmi.GetGridFaceNodes(gid, &buff[0])
        return buff

    cpdef get_grid_nodes_per_face(self, gid, np.ndarray[int, ndim=1] buff):
        self._bmi.GetGridNodesPerFace(gid, &buff[0])
        return buff

{% endif %}
