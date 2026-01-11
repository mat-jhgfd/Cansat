{
  description = "rust shell";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    fenix = {
      url = "github:nix-community/fenix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    esp-dev.url = "github:mirrexagon/nixpkgs-esp-dev";
  };

  outputs = { self, nixpkgs, flake-utils, fenix, esp-dev, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # Import nixpkgs with overlays
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ 
            fenix.overlays.default 
            esp-dev.overlays.default
            # Overlay to fix python packages (skipping failing tests)
            (final: prev: {
              python310 = prev.python310.override {
                packageOverrides = pyFinal: pyPrev: {
                  certifi = pyPrev.certifi.overridePythonAttrs (old: {
                    doCheck = false;
                  });
                  pytest-xdist = pyPrev.pytest-xdist.overridePythonAttrs (old: {
                    doCheck = false;
                  });
                };
              };
            })
          ];
        };

        # Construct LD_LIBRARY_PATH from buildInputs
        libPaths = with pkgs; [
          xorg.libX11
          xorg.libXrandr
          xorg.libXinerama
          xorg.libXcursor
          xorg.xinput
          xorg.libXi
          xorg.libXext
          libxcrypt
          glfw
          glew
          libGL
          stdenv.cc.cc.lib
        ];

        # Create LD_LIBRARY_PATH
        LD_LIBRARY_PATH_BASE = pkgs.lib.makeLibraryPath libPaths;

        # Rust toolchain
        rustToolchain = fenix.packages.${system}.stable.withComponents [
          "cargo"
          "clippy"
          "rustc"
          "rustfmt"
          "rust-src"
        ];

        # WASM target stdlib
        wasmTarget = fenix.packages.${system}.targets.wasm32-unknown-unknown.stable.rust-std;

        # Combine toolchain + target into one environment
        combinedToolchain = pkgs.symlinkJoin {
          name = "rust-toolchain-with-wasm";
          paths = [ rustToolchain wasmTarget ];
        };

        # === DEAR PYGUI BINARY BUILD ===
        # Using binary release to avoid complex C++ build issues on NixOS
        dearpygui = pkgs.python310.pkgs.buildPythonPackage rec {
            pname = "dearpygui";
            version = "2.0.0";
            format = "wheel"; 

            src = pkgs.fetchPypi rec {
                inherit pname version format;
                dist = "cp310";
                python = "cp310";
                abi = "cp310";
                platform = "manylinux1_x86_64"; 
                sha256 = "sha256-aPdJ/NNv/JzvOZ+2Sw2rWkB1xjV0FQoWMgj4IE93iFk=";
            };

            buildInputs = with pkgs; [
                xorg.libX11
                xorg.libXrandr
                xorg.libXinerama
                xorg.libXcursor
                xorg.xinput
                xorg.libXi
                xorg.libXext
                libxcrypt
                libGL
                stdenv.cc.cc.lib
            ];

            # Patch the binary wheel to use Nix store libraries
            nativeBuildInputs = [ pkgs.autoPatchelfHook ];

            doCheck = false;
            pythonImportsCheck = [ "dearpygui" ];
        };

        # Create a Python environment with Dear PyGui
        custom-python = pkgs.python310.withPackages (ps: with ps; [
            dearpygui
            pyserial
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = with pkgs; [
            # === RUST ===
            combinedToolchain
            rust-analyzer
            pkg-config
            # === PYTHON ===
            custom-python
            # === MICROPYTHON ===
            mpremote
            esptool
            adafruit-ampy
            micropython
            # === C++ ===
            gcc
            gnumake
            # === UTILS ===
            nodejs_24
          ];

          buildInputs = libPaths;

          shellHook = ''
            export PATH=${combinedToolchain}/bin:$PATH
            export RUSTC="${combinedToolchain}/bin/rustc"
            export CARGO="${combinedToolchain}/bin/cargo"
            export RUSTFLAGS="-L ${wasmTarget}/lib/rustlib/wasm32-unknown-unknown/lib"
            
            # Crucial for OpenGL/GLX on NixOS
            export LD_LIBRARY_PATH=${LD_LIBRARY_PATH_BASE}:/run/opengl-driver/lib:/run/opengl-driver-32/lib
            
            echo "Dear PyGui 2.0.0 Environment Loaded."
            echo "If GLX fails, ensure you are running on a system with hardware acceleration enabled."
            
            onefetch
            fish
          '';
        };
      }
    );
}
