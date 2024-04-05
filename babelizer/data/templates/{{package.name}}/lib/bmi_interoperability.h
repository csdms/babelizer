/*
  Function prototypes for the Fortran interoperability layer.
*/

// Max string lengths from "bmi.f90".
#define MAX_COMPONENT_NAME (2048)
#define MAX_VAR_NAME (2048)
#define MAX_TYPE_NAME (2048)
#define MAX_UNITS_NAME (2048)

int bmi_new(void);

int bmi_initialize(int model, const char *config_file, int n_chars);
int bmi_update(int model);
int bmi_update_until(int model, double until);
int bmi_finalize(int model);

int bmi_get_component_name(int model, char *name, int n_chars);
int bmi_get_input_item_count(int model, int *count);
int bmi_get_output_item_count(int model, int *count);
int bmi_get_input_var_names(int model, char **names, int n_names);
int bmi_get_output_var_names(int model, char **names, int n_names);

int bmi_get_start_time(int model, double *time);
int bmi_get_end_time(int model, double *time);
int bmi_get_current_time(int model, double *time);
int bmi_get_time_step(int model, double *time);
int bmi_get_time_units(int model, char *units, int n_chars);

int bmi_get_var_grid(int model, const char *var_name, int n_chars,
		     int *grid_id);

int bmi_get_grid_type(int model, int grid_id, char *type, int n_chars);
int bmi_get_grid_rank(int model, int grid_id, int *rank);
int bmi_get_grid_shape(int model, int grid_id, int *shape, int rank);
int bmi_get_grid_size(int model, int grid_id, int *size);
int bmi_get_grid_spacing(int model, int grid_id, double *spacing, int rank);
int bmi_get_grid_origin(int model, int grid_id, double *origin, int rank);

int bmi_get_grid_x(int model, int grid_id, double *x, int size);
int bmi_get_grid_y(int model, int grid_id, double *y, int size);
int bmi_get_grid_z(int model, int grid_id, double *z, int size);

int bmi_get_grid_node_count(int model, int grid_id, int *count);
int bmi_get_grid_edge_count(int model, int grid_id, int *count);
int bmi_get_grid_face_count(int model, int grid_id, int *count);
int bmi_get_grid_edge_nodes(int model, int grid_id, int *edge_nodes, int size);
int bmi_get_grid_face_edges(int model, int grid_id, int *face_edges, int size);
int bmi_get_grid_face_nodes(int model, int grid_id, int *face_nodes, int size);
int bmi_get_grid_nodes_per_face(int model, int grid_id,
				int *nodes_per_face, int size);

int bmi_get_var_type(int model, const char *var_name, int n_chars,
		     char *type, int m_chars);
int bmi_get_var_units(int model, const char *var_name, int n_chars,
		      char *units, int m_chars);
int bmi_get_var_itemsize(int model, const char *var_name, int n_chars,
			 int *itemsize);
int bmi_get_var_nbytes(int model, const char *var_name, int n_chars,
		       int *nbytes);
int bmi_get_var_location(int model, const char *var_name, int n_chars,
		     char *location, int m_chars);

int bmi_get_value_int(int model, const char *var_name, int n_chars,
		      void *buffer, int size);
int bmi_get_value_float(int model, const char *var_name, int n_chars,
			void *buffer, int size);
int bmi_get_value_double(int model, const char *var_name, int n_chars,
			 void *buffer, int size);

int bmi_get_value_ptr(int model, const char *var_name, int n_chars, void **ptr);

int bmi_set_value_int(int model, const char *var_name, int n_chars,
		      void *buffer, int size);
int bmi_set_value_float(int model, const char *var_name, int n_chars,
			void *buffer, int size);
int bmi_set_value_double(int model, const char *var_name, int n_chars,
			 void *buffer, int size);
