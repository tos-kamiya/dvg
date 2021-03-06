## Troubleshooting

### <a id="no-docopt" /> When I try to run dvg, I get an error message like: "ModuleNotFoundError: No module named 'docopt'".

You need to install either `docopt` or `docopt-ng` package. Run `pip3 install docopt-ng`.

### <a id="command-not-found" /> When I try to run dvg, I get an error message like "dvg: command not found ".

The `dvg` executable does not seem on PATH.

If you are using Windows, check the PATH variable in Advanced system settings -> Environment Variables.
Make sure `C:\Users\<username>\AppData\Local\Programs\Python\Python39\Scripts\` (the path may differ depending on the version of Python you are running) is included.

If you are using macOS, check the PATH variable in `~/.zprofile` .
Make sure `~/Python/3.8/bin` (the path may differ depending on the version of Python you are running) is included.

If you are using Ubuntu, check the PATH variable in shell configuration files, such as `~/.profile`, `~/.bashrc`, etc. Make sure `~/.local/bin` is included.

If you do not want to set the PATH environment variable for some reason, you can still run the dvg scripts:

```sh
python3 -m dvg dvg ...  # Runs the dvg script
```

```sh
python3 -m dvg dvgi ...  # Runs the dvgi script
```

### <a id="none-of-pytorch" /> While running dvg, a warning message "None of PyTorch, TensorFlow >= 2.0, or Flax have been found..." appears.

Please install PyTorch as described in the installation instructions.

