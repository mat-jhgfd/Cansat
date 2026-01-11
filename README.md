# Organisation
This project has 2 ui. The rust one is outdated and replaced with the new python one.
```
.
├── bme280.py
├── Cargo.lock
├── Cargo.toml
├── flake.lock
├── flake.nix
├── main.py
├── micropyGPS.py
├── README.md
├── rfm69.py
├── src
│   ├── app.rs
│   ├── graph
│   │   ├── config.rs
│   │   ├── data.rs
│   │   └── shared.rs
│   ├── graph.rs
│   ├── main.rs
│   ├── net
│   │   └── remote.rs
│   ├── net.rs
│   ├── panels
│   │   ├── graph.rs
│   │   ├── history.rs
│   │   ├── info.rs
│   │   ├── paragraph.rs
│   │   └── title.rs
│   ├── panels.rs
│   ├── ui
│   │   └── node.rs
│   └── ui.rs
├── test_receiver_matteo.py
├── test_tobias.py
└── v0.1
    ├── test_3_base_ui.py
    ├── test_3_b_graphs.py
    ├── test_3_left_menu.py
    └── test-3.py
```
# How to use python ui (actual)
```shell
python test_3.py
```

# How to use rust ui (outdated)
this works only with the official CanSat code almost not modified.
use this to use the app
```shell
cargo run --release
```
or
```shell
cargo r -r
```
It's the same

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
There is documentation in the whole code.
## rust
Check well the src/app.rs documentation for the rust code.
To view the documentation code ```///``` and ```//!``` better use
```shell
cargo doc --open
```
## python
There are comment to help.
