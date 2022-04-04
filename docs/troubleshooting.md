## Troubleshooting

### <a id="command-not-found" /> When I try to run dvg, I get an error message like "dvg: command not found ".

The `dvg` executable does not seem on PATH.

If you are using Windows, check the PATH variable in Advanced system settings -> Environment Variables.

If you are using macOS, check the PATH variable in `.zprofile` .

If you do not want to set the PATH environment variable for some reason, you can still run the dvg scripts:

```sh
python3 -m dvg dvg ...  # Runs the dvg script
```

```sh
python3 -m dvg dvgi ...  # Runs the dvgi script
```

### <a id="none-of-pytorch" /> While running dvg, a warning message "None of PyTorch, TensorFlow >= 2.0, or Flax have been found..." appears.

Please install PyTorch as described in the installation instructions.

