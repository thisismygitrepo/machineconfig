F821 Undefined name `get_all_dicts`
  --> src/machineconfig/scripts/python/devops_devapps_install.py:45:74
   |
44 |     # interactive installation
45 |     installers = [Installer.from_dict(d=vd, name=name) for __kat, vds in get_all_dicts(system=system()).items() for name, vd in vds.it…
   |                                                                          ^^^^^^^^^^^^^
46 |
47 |     # Check installed programs with progress indicator
   |

Found 1 error.
