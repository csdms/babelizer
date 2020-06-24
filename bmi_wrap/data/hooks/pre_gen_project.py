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


{%- for entry_point in cookiecutter.entry_points.split(',') %}
if not is_valid_entry_point("{{ entry_point }}"):
    print(
        "ERROR: The entry point (%s) is not a valid Python entry point."
        % "{{ entry_point }}"
    )

    sys.exit(2)
{% endfor %}
