import subprocess


def tests_bake_with_defaults():
    subprocess.check_call(['cookiecutter', '.', '--no-input'])
