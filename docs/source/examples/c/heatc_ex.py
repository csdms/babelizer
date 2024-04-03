"""An example of running the C heat model through its BMI."""

import numpy as np
from pymt_heatc import HeatC

config_file = "config.txt"
np.set_printoptions(formatter={"float": "{: 6.1f}".format})


# Instatiate an initialize the model.
m = HeatC()
print(m.get_component_name())
m.initialize(config_file)

# List the model's exchange items.
print("Input vars:", m.get_input_var_names())
print("Output vars:", m.get_output_var_names())

# Get the grid_id for the plate_surface__temperature variable.
var_name = "plate_surface__temperature"
print(f"Variable {var_name}")
grid_id = m.get_var_grid(var_name)
print(" - grid id:", grid_id)

# Get grid and variable info for plate_surface__temperature.
print(" - grid type:", m.get_grid_type(grid_id))
grid_rank = m.get_grid_rank(grid_id)
print(" - rank:", grid_rank)
grid_shape = np.empty(grid_rank, dtype=np.int32)
m.get_grid_shape(grid_id, grid_shape)
print(" - shape:", grid_shape)
grid_size = m.get_grid_size(grid_id)
print(" - size:", grid_size)
grid_spacing = np.empty(grid_rank, dtype=np.float64)
m.get_grid_spacing(grid_id, grid_spacing)
print(" - spacing:", grid_spacing)
grid_origin = np.empty(grid_rank, dtype=np.float64)
m.get_grid_origin(grid_id, grid_origin)
print(" - origin:", grid_origin)
print(" - variable type:", m.get_var_type(var_name))
print(" - units:", m.get_var_units(var_name))
print(" - itemsize:", m.get_var_itemsize(var_name))
print(" - nbytes:", m.get_var_nbytes(var_name))

# Get the initial temperature values.
val = np.empty(grid_shape, dtype=np.float64)
m.get_value(var_name, val)
print(" - initial values (gridded):")
print(val.reshape(np.roll(grid_shape, 1)))

# Get time information from the model.
print("Start time:", m.get_start_time())
print("End time:", m.get_end_time())
print("Current time:", m.get_current_time())
print("Time step:", m.get_time_step())
print("Time units:", m.get_time_units())

# Advance the model by one time step.
m.update()
print("Updated time:", m.get_current_time())

# Advance the model until a later time.
m.update_until(5.0)
print("Later time:", m.get_current_time())

# Finalize the model.
m.finalize()
