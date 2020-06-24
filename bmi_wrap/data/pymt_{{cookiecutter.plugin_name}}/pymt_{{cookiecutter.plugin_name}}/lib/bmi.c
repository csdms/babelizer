#include <stdlib.h>
#include "bmi.h"

static BMI_Model* bmi_new() {
  return (BMI_Model*) calloc(1, sizeof(BMI_Model));
}


static int bmi_initialize(BMI_Model* model, const char *config_file,
    void**self) {
  return model->initialize(config_file, &(model->self));
}


static int bmi_update(BMI_Model* model) {
  return model->update(model->self);
}


static int bmi_update_until(BMI_Model* model, double until) {
  return model->update_until(model->self, until);
}


static int bmi_update_frac(BMI_Model* model, double frac) {
  return model->update_frac(model->self, frac);
}


static int bmi_finalize(BMI_Model* model) {
  return model->finalize(model->self);
}


static int bmi_run_model(BMI_Model* model) {
  return model->run_model(model->self);
}


static int bmi_get_component_name(BMI_Model* model, char* name) {
  return model->get_component_name(model->self, name);
}


static int bmi_get_input_var_name_count(BMI_Model* model, int *count) {
  return model->get_input_var_name_count(model->self, count);
}


static int bmi_get_output_var_name_count(BMI_Model* model, int *count) {
  return model->get_output_var_name_count(model->self, count);
}


static int bmi_get_input_var_names(BMI_Model* model, char **names) {
  return model->get_input_var_names(model->self, names);
}


static int bmi_get_output_var_names(BMI_Model* model, char **names) {
  return model->get_output_var_names(model->self, names);
}


static int bmi_get_var_grid(BMI_Model* model, const char *name, int *gid) {
  return model->get_var_grid(model->self, name, gid);
}


static int bmi_get_var_type(BMI_Model* model, const char *name, char *dtype) {
  return model->get_var_type(model->self, name, dtype);
}


static int bmi_get_var_units(BMI_Model* model, const char *name, char *units) {
  return model->get_var_units(model->self, name, units);
}


static int bmi_get_var_itemsize(BMI_Model* model, const char *name, int *itemsize) {
  return model->get_var_itemsize(model->self, name, itemsize);
}


static int bmi_get_var_nbytes(BMI_Model* model, const char *name, int *nbytes) {
  return model->get_var_nbytes(model->self, name, nbytes);
}


static int bmi_get_var_location(BMI_Model* model, const char *name, char *location) {
  return model->get_var_location(model->self, name, location);
}


static int bmi_get_current_time(BMI_Model* model, double* time) {
  return model->get_current_time(model->self, time);
}


static int bmi_get_start_time(BMI_Model* model, double* time) {
  return model->get_start_time(model->self, time);
}


static int bmi_get_end_time(BMI_Model* model, double* time) {
  return model->get_end_time(model->self, time);
}


static int bmi_get_time_units(BMI_Model* model, char* units) {
  return model->get_time_units(model->self, units);
}


static int bmi_get_time_step(BMI_Model* model, double* time) {
  return model->get_time_step(model->self, time);
}


static int bmi_get_value(BMI_Model* model, const char* name, void * buffer) {
  return model->get_value(model->self, name, buffer);
}


static int bmi_get_value_ptr(BMI_Model* model, const char* name, void ** ptr) {
  return model->get_value_ptr(model->self, name, ptr);
}


static int bmi_set_value(BMI_Model* model, const char* name, void *buffer) {
  return model->set_value(model->self, name, buffer);
}


static int bmi_get_grid_rank(BMI_Model* model, int gid, int *rank) {
  return model->get_grid_rank(model->self, gid, rank);
}


static int bmi_get_grid_size(BMI_Model* model, int gid, int *size) {
  return model->get_grid_size(model->self, gid, size);
}


static int bmi_get_grid_type(BMI_Model* model, int gid, char *gtype) {
  return model->get_grid_type(model->self, gid, gtype);
}


static int bmi_get_grid_shape(BMI_Model* model, int gid, int* shape) {
  return model->get_grid_shape(model->self, gid, shape);
}

static int bmi_get_grid_spacing(BMI_Model* model, int gid, double* spacing) {
  return model->get_grid_spacing(model->self, gid, spacing);
}


static int bmi_get_grid_origin(BMI_Model* model, int gid, double* origin) {
  return model->get_grid_origin(model->self, gid, origin);
}


/*

  int (* get_grid_x)(void *, int, double *);
  int (* get_grid_y)(void *, int, double *);
  int (* get_grid_z)(void *, int, double *);

  int (* get_grid_face_count)(void *, int, int *);
  int (* get_grid_point_count)(void *, int, int *);
  int (* get_grid_vertex_count)(void *, int, int *);

  int (* get_grid_connectivity)(void *, int, int *);
  int (* get_grid_offset)(void *, int, int *);
*/
