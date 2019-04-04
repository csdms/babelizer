!
! This is the interoperability layer for the Fortran BMI.
!
module bmi_interoperability

{%- set entry_point = cookiecutter.entry_points.split(',')[0] %}
{%- set pymt_class = entry_point.split('=')[0] %}
{%- set plugin_module, plugin_class = entry_point.split('=')[1].split(':') %}

  use, intrinsic :: iso_c_binding
  use bmif

{%- if cookiecutter.libraries %}
{%- for lib in cookiecutter.libraries.split(',') %}
  use {{ lib }}
{%- endfor %}
{%- endif %}
  use {{ plugin_module }}

  implicit none

  integer, parameter :: N_MODELS = 2048
  type ({{ plugin_class }}) :: model_array(N_MODELS)
  logical :: model_avail(N_MODELS) = .true.

contains

  !
  ! Find the next unused model index in the array.
  !
  function bmi_new() bind(c) result(model_index)
    integer (c_int) :: model_index
    integer :: i

    model_index = -1
    do i = 1, N_MODELS
       if (model_avail(i)) then
          model_avail(i) = .false.
          model_index = i
          exit
       end if
    end do
  end function bmi_new

  !
  ! Initialize one model in the array, based on the input index.
  !
  function bmi_initialize(model_index, config_file, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: config_file(n)
    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: config_file_

    ! Convert `config_file` from rank-1 array to scalar.
    do i = 1, n
       config_file_(i:i) = config_file(i)
    enddo

    status = model_array(model_index)%initialize(config_file_)
  end function bmi_initialize

  !
  ! Clean up one model in the array.
  !
  function bmi_finalize(model_index) bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int) :: status

    status = model_array(model_index)%finalize()
    model_avail(model_index) = .true.
  end function bmi_finalize

  !
  ! Get the component name attribute.
  !
  function bmi_get_component_name(model_index, name, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(out) :: name(n)

    integer (c_int) :: i, status
    character (len=n, kind=c_char), pointer :: pname
    character (len=n, kind=c_char) :: name_

    status = model_array(model_index)%get_component_name(pname)

    ! Cast `pname` back to a string, dereferences `pname`.
    name_ = pname

    ! Load the `name_` string, trimmed, back into `name` for output.
    do i = 1, len(trim(name_))
        name(i) = name_(i:i)
    enddo
    name = name//C_NULL_CHAR
  end function bmi_get_component_name

  !
  ! Get the number of input variables.
  !
  function bmi_get_input_var_name_count(model_index, count) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(out) :: count
    integer (c_int) :: status
    character (len=BMI_MAX_VAR_NAME), pointer :: pnames(:)

    status = model_array(model_index)%get_input_var_names(pnames)
    count = size(pnames)
    status = BMI_SUCCESS
  end function bmi_get_input_var_name_count

  !
  ! Get the names of the input variables.
  !
  function bmi_get_input_var_names(model_index, names, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    type (c_ptr),  intent(out) :: names(n)
    integer (c_int) :: status, i
    character (len=BMI_MAX_VAR_NAME), dimension(:), pointer :: pnames

    status = model_array(model_index)%get_input_var_names(pnames)

    do i = 1, n
       pnames(i) = trim(pnames(i))//C_NULL_CHAR
       names(i) = c_loc(pnames(i))
    enddo
  end function bmi_get_input_var_names

  !
  ! Get the number of output variables.
  !
  function bmi_get_output_var_name_count(model_index, count) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(out) :: count
    integer (c_int) :: status
    character (len=BMI_MAX_VAR_NAME), pointer :: pnames(:)

    status = model_array(model_index)%get_output_var_names(pnames)
    count = size(pnames)
    status = BMI_SUCCESS
  end function bmi_get_output_var_name_count

  !
  ! Get the names of the output variables.
  !
  function bmi_get_output_var_names(model_index, names, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    type (c_ptr),  intent(out) :: names(n)
    integer (c_int) :: status, i
    character (len=BMI_MAX_VAR_NAME), dimension(:), pointer :: pnames

    status = model_array(model_index)%get_output_var_names(pnames)

    do i = 1, n
       pnames(i) = trim(pnames(i))//C_NULL_CHAR
       names(i) = c_loc(pnames(i))
    enddo
  end function bmi_get_output_var_names

  !
  ! Get the model start time.
  !
  function bmi_get_start_time(model_index, time) bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    real (c_double), intent(out) :: time
    integer (c_int) :: status

    status = model_array(model_index)%get_start_time(time)
  end function bmi_get_start_time

  !
  ! Get the model stop time.
  !
  function bmi_get_end_time(model_index, time) bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    real (c_double), intent(out) :: time
    integer (c_int) :: status

    status = model_array(model_index)%get_end_time(time)
  end function bmi_get_end_time

  !
  ! Get the current model time.
  !
  function bmi_get_current_time(model_index, time) bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    real (c_double), intent(out) :: time
    integer (c_int) :: status

    status = model_array(model_index)%get_current_time(time)
  end function bmi_get_current_time

  !
  ! Get the model time step.
  !
  function bmi_get_time_step(model_index, time_step) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    real (c_double), intent(out) :: time_step
    integer (c_int) :: status

    status = model_array(model_index)%get_time_step(time_step)
  end function bmi_get_time_step

  !
  ! Get the model time units.
  !
  function bmi_get_time_units(model_index, time_units, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(out) :: time_units(n)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: time_units_

    ! Convert `time_units` from rank-1 array to scalar.
    do i = 1, n
       time_units_(i:i) = time_units(i)
    enddo

    status = model_array(model_index)%get_time_units(time_units_)

    ! Load the `time_units_` result back into `time_units` for output.
    do i = 1, len(trim(time_units_))
        time_units(i) = time_units_(i:i)
    enddo
    time_units = time_units//C_NULL_CHAR
  end function bmi_get_time_units

  !
  ! Advance the model by one time step.
  !
  function bmi_update(model_index) bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int) :: status

    status = model_array(model_index)%update()
  end function bmi_update

  !
  ! Advance the model by a fraction of a time step.
  !
  function bmi_update_frac(model_index, time_frac) bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    real (c_double), intent(in), value :: time_frac
    integer (c_int) :: status

    status = model_array(model_index)%update_frac(time_frac)
  end function bmi_update_frac

  !
  ! Advance the model to a time in the future.
  !
  function bmi_update_until(model_index, time_later) bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    real (c_double), intent(in), value :: time_later
    integer (c_int) :: status

    status = model_array(model_index)%update_until(time_later)
  end function bmi_update_until

  !
  ! Get the grid identifier for a given variable.
  !
  function bmi_get_var_grid(model_index, var_name, n, grid_id) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(out) :: grid_id
    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_

    ! Convert `var_name` from rank-1 array to scalar.
    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%get_var_grid(var_name_, grid_id)
  end function bmi_get_var_grid

  !
  ! Get the grid type for the specified variable.
  !
  function bmi_get_grid_type(model_index, grid_id, grid_type, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(out) :: grid_type(n)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: grid_type_

    do i = 1, n
       grid_type_(i:i) = grid_type(i)
    enddo

    status = model_array(model_index)%get_grid_type(grid_id, grid_type_)

    do i = 1, len(trim(grid_type_))
        grid_type(i) = grid_type_(i:i)
    enddo
    grid_type = grid_type//C_NULL_CHAR
  end function bmi_get_grid_type

  !
  ! Get the number of dimensions of a grid.
  !
  function bmi_get_grid_rank(model_index, grid_id, grid_rank) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(out) :: grid_rank
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_rank(grid_id, grid_rank)
  end function bmi_get_grid_rank

  !
  ! Get the dimensions of a grid.
  !
  function bmi_get_grid_shape(model_index, grid_id, grid_shape, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(in), value :: n
    integer (c_int), intent(out) :: grid_shape(n)
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_shape(grid_id, grid_shape)
  end function bmi_get_grid_shape

  !
  ! Get the total number of elements in a grid.
  !
  function bmi_get_grid_size(model_index, grid_id, grid_size) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(out) :: grid_size
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_size(grid_id, grid_size)
  end function bmi_get_grid_size

  !
  ! Get the spacing between grid elements in each dimension.
  !
  function bmi_get_grid_spacing(model_index, grid_id, grid_spacing, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(in), value :: n
    real (c_double), intent(out) :: grid_spacing(n)
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_spacing(grid_id, grid_spacing)
  end function bmi_get_grid_spacing

  !
  ! Get the origin of the grid.
  !
  function bmi_get_grid_origin(model_index, grid_id, grid_origin, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(in), value :: n
    real (c_double), intent(out) :: grid_origin(n)
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_origin(grid_id, grid_origin)
  end function bmi_get_grid_origin

  !
  ! Get the x-coordinates of a grid's nodes.
  !
  function bmi_get_grid_x(model_index, grid_id, grid_x, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(in), value :: n
    real (c_double), intent(out) :: grid_x(n)
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_x(grid_id, grid_x)
  end function bmi_get_grid_x

  !
  ! Get the y-coordinates of a grid's nodes.
  !
  function bmi_get_grid_y(model_index, grid_id, grid_y, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(in), value :: n
    real (c_double), intent(out) :: grid_y(n)
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_y(grid_id, grid_y)
  end function bmi_get_grid_y

  !
  ! Get the z-coordinates of a grid's nodes.
  !
  function bmi_get_grid_z(model_index, grid_id, grid_z, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(in), value :: n
    real (c_double), intent(out) :: grid_z(n)
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_z(grid_id, grid_z)
  end function bmi_get_grid_z

  !
  ! Get the connectivity of a grid's nodes.
  !
  function bmi_get_grid_connectivity(model_index, grid_id, grid_conn, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(in), value :: n
    integer (c_int), intent(out) :: grid_conn(n)
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_connectivity(grid_id, grid_conn)
  end function bmi_get_grid_connectivity

  !
  ! Get the offset of a grid's nodes.
  !
  function bmi_get_grid_offset(model_index, grid_id, grid_offset, n) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: grid_id
    integer (c_int), intent(in), value :: n
    integer (c_int), intent(out) :: grid_offset(n)
    integer (c_int) :: status

    status = model_array(model_index)%get_grid_offset(grid_id, grid_offset)
  end function bmi_get_grid_offset

  !
  ! Get the type for the specified variable.
  !
  function bmi_get_var_type(model_index, var_name, n, var_type, m) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(in), value :: m
    character (len=1, kind=c_char), intent(out) :: var_type(m)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_
    character (len=m, kind=c_char) :: var_type_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo
    do i = 1, m
       var_type_(i:i) = var_type(i)
    enddo

    status = model_array(model_index)%get_var_type(var_name_, var_type_)

    do i = 1, len(trim(var_type_))
        var_type(i) = var_type_(i:i)
    enddo
    var_type = var_type//C_NULL_CHAR
  end function bmi_get_var_type

  !
  ! Get the units for the specified variable.
  !
  function bmi_get_var_units(model_index, var_name, n, var_units, m) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(in), value :: m
    character (len=1, kind=c_char), intent(out) :: var_units(m)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_
    character (len=m, kind=c_char) :: var_units_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo
    do i = 1, m
       var_units_(i:i) = var_units(i)
    enddo

    status = model_array(model_index)%get_var_units(var_name_, var_units_)

    do i = 1, len(trim(var_units_))
        var_units(i) = var_units_(i:i)
    enddo
    var_units = var_units//C_NULL_CHAR
  end function bmi_get_var_units

  !
  ! Get the size of a single element of the specified variable.
  !
  function bmi_get_var_itemsize(model_index, var_name, n, var_itemsize) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(out) :: var_itemsize

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%get_var_itemsize(var_name_, var_itemsize)
  end function bmi_get_var_itemsize

  !
  ! Get the total number of bytes used by the specified variable.
  !
  function bmi_get_var_nbytes(model_index, var_name, n, var_nbytes) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(out) :: var_nbytes

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%get_var_nbytes(var_name_, var_nbytes)
  end function bmi_get_var_nbytes

  !
  ! Get a copy of an integer variable's values, flattened.
  !
  function bmi_get_value_int(model_index, var_name, n, buffer, m) &
       bind(c) result(status) ! (2)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(in), value :: m
    integer (c_int), intent(out) :: buffer(m) ! (1)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%get_value(var_name_, buffer)
  end function bmi_get_value_int

  !
  ! Get a copy of a float variable's values, flattened.
  !
  function bmi_get_value_float(model_index, var_name, n, buffer, m) &
       bind(c) result(status) ! (2)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(in), value :: m
    real (c_float), intent(out) :: buffer(m)  ! (1)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%get_value(var_name_, buffer)
    ! write(*,*) "Fortran"
    ! write(*,'(8f6.2)') buffer
    ! write(*,'(48f6.1)') buffer

    ! (1) Can't have assumed-shape array `buffer(:)` with bind(c).
    ! (2) Can't have type-bound (therefore generic) procedures with bind(c).
  end function bmi_get_value_float

  !
  ! Get a copy of a double precision variable's values, flattened.
  !
  function bmi_get_value_double(model_index, var_name, n, buffer, m) &
       bind(c) result(status) ! (2)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(in), value :: m
    real (c_double), intent(out) :: buffer(m)  ! (1)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%get_value(var_name_, buffer)
  end function bmi_get_value_double

  !
  ! Get a reference to a variable's values.
  !
  function bmi_get_value_ptr(model_index, var_name, n, ref) &
       bind(c) result(status)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    type (c_ptr), intent(out) :: ref

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_
    character (len=BMI_MAX_TYPE_NAME, kind=c_char) :: var_type
    integer, pointer :: idest(:)
    real, pointer :: rdest(:)
    double precision, pointer :: ddest(:)

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%get_var_type(var_name_, var_type)

    select case(var_type)
    case("integer")
       status = model_array(model_index)%get_value_ptr(var_name_, idest)
       ref = c_loc(idest(1))
       status = BMI_SUCCESS
    case("real")
       status = model_array(model_index)%get_value_ptr(var_name_, rdest)
       ref = c_loc(rdest(1))
       status = BMI_SUCCESS
    case("double precision")
       status = model_array(model_index)%get_value_ptr(var_name_, ddest)
       ref = c_loc(ddest(1))
       status = BMI_SUCCESS
    case default
       status = BMI_FAILURE
    end select
  end function bmi_get_value_ptr

  !
  ! Set an integer variable's values.
  !
  function bmi_set_value_int(model_index, var_name, n, buffer, m) &
       bind(c) result(status) ! (2)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(in), value :: m
    integer (c_int), intent(in) :: buffer(m) ! (1)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%set_value(var_name_, buffer)
  end function bmi_set_value_int

  !
  ! Set a float variable's values.
  !
  function bmi_set_value_float(model_index, var_name, n, buffer, m) &
       bind(c) result(status) ! (2)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(in), value :: m
    real (c_float), intent(in) :: buffer(m) ! (1)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%set_value(var_name_, buffer)

    ! (1) Can't have assumed-shape array `buffer(:)` with bind(c).
    ! (2) Can't have type-bound (therefore generic) procedures with bind(c).
  end function bmi_set_value_float

  !
  ! Set a double precision variable's values.
  !
  function bmi_set_value_double(model_index, var_name, n, buffer, m) &
       bind(c) result(status) ! (2)
    integer (c_int), intent(in), value :: model_index
    integer (c_int), intent(in), value :: n
    character (len=1, kind=c_char), intent(in) :: var_name(n)
    integer (c_int), intent(in), value :: m
    real (c_double), intent(in) :: buffer(m) ! (1)

    integer (c_int) :: i, status
    character (len=n, kind=c_char) :: var_name_

    do i = 1, n
       var_name_(i:i) = var_name(i)
    enddo

    status = model_array(model_index)%set_value(var_name_, buffer)
  end function bmi_set_value_double

end module bmi_interoperability
