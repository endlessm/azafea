import os


# The Python documentation for os.cpu_count() says:
#
#     Return the number of CPUs in the system. Returns None if undetermined.
#
# This makes sure to always return an integer.
def get_cpu_count() -> int:
    return os.cpu_count() or 1
