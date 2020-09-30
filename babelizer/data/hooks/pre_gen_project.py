import re
import sys


MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"

module_name = "{{ cookiecutter.plugin_name }}"


if not re.match(MODULE_REGEX, module_name):
    print(
        "ERROR: The project slug (%s) is not a valid Python module name. Please do not use a - and use _ instead"
        % module_name
    )

    # Exit to cancel project
    sys.exit(1)


def is_valid_entry_point(entry_point):
    try:
        pymt_class, plugin_entry_point = entry_point.split("=")
    except ValueError:
        return False
    try:
        plugin_module, plugin_class = plugin_entry_point.split(":")
    except ValueError:
        return False

    if not re.match(MODULE_REGEX, pymt_class):
        return False
    for module_name in plugin_module.split("."):
        if not re.match(MODULE_REGEX, module_name):
            return False
    if not re.match(MODULE_REGEX, plugin_class):
        return False

    return True


{%- for pymt_class, component in cookiecutter.components|dictsort %}
if not is_valid_entry_point(entry_point := "{{ pymt_class }}={{ component.library }}:{{ component.class}}"):
    print(f"ERROR: The entry point ({entry_point}) is not a valid Python entry point.")

    sys.exit(2)
{% endfor %}
