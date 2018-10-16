
{% if cookiecutter.language == 'c' %}

cdef extern from "bmi.h":
    ctypedef struct BMI_Model:
        pass
{% for entry_point in cookiecutter.entry_points.split(',') %}
    {%- set plugin_module, bmi_register = entry_point.split('=')[1].split(':') %}
    BMI_Model* {{ bmi_register }}(BMI_Model *model)
{%- endfor %}
{% elif cookiecutter.language == 'c++' %}

cdef extern from "bmi.hxx" namespace "bmi":
    cdef cppclass Model:
        Model() except +
        void GetComponentName(char * name) except +
        int GetInputVarNameCount() except +
        int GetOutputVarNameCount() except +
        void GetInputVarNames(char** names) except +
        void GetOutputVarNames(char** names) except +

        void Initialize (const char * config_file) except +
        void Update() except +
        void UpdateUntil(double time) except +
        void Finalize() except +

        int GetVarGrid (const char * var_name) except +
        void GetVarType (const char * var_name, char * const vtype) except +
        void GetVarUnits (const char * var_name, char * const units) except +
        int GetVarItemsize(const char * name) except +
        int GetVarNbytes(const char * name) except +
        void GetVarLocation(const char * var_name, char * const location) except +

        double GetCurrentTime () except +
        double GetStartTime () except +
        double GetEndTime () except +
        double GetTimeStep () except +
        void GetTimeUnits (char * const units) except +

        void GetValue (const char * var_name, void *buffer) except +
        void SetValue (const char * var_name, void *buffer) except +

        void GetGridType (const int grid_id, char * const gtype) except +
        int GetGridRank (const int grid_id) except +
        int GetGridSize (const int grid_id) except +

        void GetGridX (const int gid, double * const x) except +
        void GetGridY (const int gid, double * const y) except +

        # int GetGridNumberOfEdges(const int)
        int GetGridNumberOfFaces(const int) except +
        
        void GetGridEdgeNodes(const int, int * const) except +
        void GetGridFaceEdges(const int, int * const) except +
        void GetGridFaceNodes(const int, int * const) except +
        void GetGridNodesPerFace(const int, int * const) except +

{% endif %}
