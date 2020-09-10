#include <stdlib.h>
#include "bmi.h"


static int bmi_initialize(Bmi* model, const char *config_file) {
  return model->initialize(model, config_file);
}


static int bmi_update(Bmi* model) {
  return model->update(model);
}


static int bmi_update_until(Bmi* model, double until) {
  return model->update_until(model, until);
}

/*
static int bmi_update_frac(Bmi* model, double frac) {
  return model->update_frac(model, frac);
}
*/

static int bmi_finalize(Bmi* model) {
  return model->finalize(model);
}

/*
static int bmi_run_model(Bmi* model) {
  return model->run_model(model);
}
*/

static int bmi_get_component_name(Bmi* model, char* name) {
  return model->get_component_name(model, name);
}


static int bmi_get_input_item_count(Bmi* model, int *count) {
  return model->get_input_item_count(model, count);
}


static int bmi_get_output_item_count(Bmi* model, int *count) {
  return model->get_output_item_count(model, count);
}


static int bmi_get_input_var_names(Bmi* model, char **names) {
  return model->get_input_var_names(model, names);
}


static int bmi_get_output_var_names(Bmi* model, char **names) {
  return model->get_output_var_names(model, names);
}


static int bmi_get_var_grid(Bmi* model, const char *name, int *gid) {
  return model->get_var_grid(model, name, gid);
}


static int bmi_get_var_type(Bmi* model, const char *name, char *dtype) {
  return model->get_var_type(model, name, dtype);
}


static int bmi_get_var_units(Bmi* model, const char *name, char *units) {
  return model->get_var_units(model, name, units);
}


static int bmi_get_var_itemsize(Bmi* model, const char *name, int *itemsize) {
  return model->get_var_itemsize(model, name, itemsize);
}


static int bmi_get_var_nbytes(Bmi* model, const char *name, int *nbytes) {
  return model->get_var_nbytes(model, name, nbytes);
}


static int bmi_get_var_location(Bmi* model, const char *name, char *location) {
  return model->get_var_location(model, name, location);
}


static int bmi_get_current_time(Bmi* model, double* time) {
  return model->get_current_time(model, time);
}


static int bmi_get_start_time(Bmi* model, double* time) {
  return model->get_start_time(model, time);
}


static int bmi_get_end_time(Bmi* model, double* time) {
  return model->get_end_time(model, time);
}


static int bmi_get_time_units(Bmi* model, char* units) {
  return model->get_time_units(model, units);
}


static int bmi_get_time_step(Bmi* model, double* time) {
  return model->get_time_step(model, time);
}


static int bmi_get_value(Bmi* model, const char* name, void * buffer) {
  return model->get_value(model, name, buffer);
}


static int bmi_get_value_ptr(Bmi* model, const char* name, void ** ptr) {
  return model->get_value_ptr(model, name, ptr);
}

static int bmi_get_value_at_indices(Bmi* model, const char* name, void * dest, int *inds, int count) {
  return model->get_value_at_indices(model, name, dest, inds, count);
}


static int bmi_set_value(Bmi* model, const char* name, void *src) {
  return model->set_value(model, name, src);
}

static int bmi_set_value_at_indices(Bmi* model, const char* name, int *inds, int count, void *src) {
  return model->set_value_at_indices(model, name, inds, count, src);
}


static int bmi_get_grid_rank(Bmi* model, int gid, int *rank) {
  return model->get_grid_rank(model, gid, rank);
}


static int bmi_get_grid_size(Bmi* model, int gid, int *size) {
  return model->get_grid_size(model, gid, size);
}


static int bmi_get_grid_type(Bmi* model, int gid, char *gtype) {
  return model->get_grid_type(model, gid, gtype);
}


static int bmi_get_grid_shape(Bmi* model, int gid, int* shape) {
  return model->get_grid_shape(model, gid, shape);
}

static int bmi_get_grid_spacing(Bmi* model, int gid, double* spacing) {
  return model->get_grid_spacing(model, gid, spacing);
}


static int bmi_get_grid_origin(Bmi* model, int gid, double* origin) {
  return model->get_grid_origin(model, gid, origin);
}


static int bmi_get_grid_x(Bmi *model, int grid, double *x) {
  return model->get_grid_x(model, grid, x);
}


static int bmi_get_grid_y(Bmi *model, int grid, double *y) {
  return model->get_grid_y(model, grid, y);
}


static int bmi_get_grid_z(Bmi *model, int grid, double *z) {
  return model->get_grid_z(model, grid, z);
}

static int bmi_get_grid_node_count(Bmi *model, int grid, int *count) {
  return model->get_grid_node_count(model, grid, count);
}


static int bmi_get_grid_edge_count(Bmi *model, int grid, int *count) {
  return model->get_grid_edge_count(model, grid, count);
}


static int bmi_get_grid_face_count(Bmi *model, int grid, int *count) {
  return model->get_grid_face_count(model, grid, count);
}


static int bmi_get_grid_edge_nodes(Bmi *model, int grid, int *edge_nodes) {
  return model->get_grid_edge_nodes(model, grid, edge_nodes);
}


static int bmi_get_grid_face_edges(Bmi *model, int grid, int *face_edges) {
  return model->get_grid_face_edges(model, grid, face_edges);
}


static int bmi_get_grid_face_nodes(Bmi *model, int grid, int *face_nodes) {
  return model->get_grid_face_nodes(model, grid, face_nodes);
}


static int bmi_get_grid_nodes_per_face(Bmi *model, int grid, int *nodes_per_face) {
  return model->get_grid_nodes_per_face(model, grid, nodes_per_face);
}
