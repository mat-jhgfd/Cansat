# Organisation
Tree of the project
```
.
├── code_on_cansat
│   ├── bme280.py
│   ├── config.py
│   ├── gps.py
│   ├── hardware.py
│   ├── logger_init.py
│   ├── main.py
│   ├── micropyGPS.py
│   ├── radio.py
│   ├── rfm69.py
│   ├── sensors.py
│   └── test_tobias.py
├── flake.lock
├── flake.nix
├── README.md
├── test_receiver_matteo.py
└── v0.1
    ├── graph_update.py
    ├── http_server.py
    ├── serial_reader.py
    ├── shared_state.py
    ├── test_3_base_ui.py
    ├── test_3_b_graphs.py
    ├── test_3_left_menu.py
    ├── test-3.py
    └── ui_setup.py
```
# How to use python ui
```shell
python test_3.py
```

# Useful commands
```shell
sudo mpremote rm -r logs_files/ && sudo mpremote mkdir logs_files/
```
^ This 'reset' the logs folder on the pico by removing it and readding it.
```shell
sudo mpremote ls logs_files/
```
^ This list all the logs files.
```shell
sudo mpremote cat logs_files/log_#.txt | less
```
^ This make you see the files without transferring it in your machine.
```shell
sudo ampy --port /dev/ttyACM0 put file.py
```
^ This transfer a file from your machine to the pico

# For documentation
```
## python
There are comment to help.
