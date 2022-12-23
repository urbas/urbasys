{
  description = "A set of tools to support my home automation setup.";

  inputs.nixpkgs.url = "nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs, ... }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
      forSupportedSystems = f: with nixpkgs.lib; foldl' (resultAttrset: system: recursiveUpdate resultAttrset (f { inherit system; pkgs = import nixpkgs { inherit system; }; })) {} supportedSystems;

    in forSupportedSystems ({ pkgs, system, ... }: with pkgs;
      let
        checkInputs = with python3Packages; [
          pytest-cov
          pytestCheckHook
        ];

        propagatedBuildInputs = with python3Packages; [
          click
          requests
        ];

        devInputs = with python3Packages; [
          black
          flake8
          pytest
          pytest-watch
        ];

        pyEnv = python3.withPackages(_: checkInputs ++ devInputs ++ propagatedBuildInputs);

        devEnv = stdenvNoCC.mkDerivation {
          name = "devEnv";
          buildInputs = [ pyEnv ];
        };

        pkg = python3Packages.buildPythonPackage {
          pname = "urbasys";
          version = "local";
          src = lib.cleanSourceWith { src = ./.; };
          inherit checkInputs propagatedBuildInputs;
        };

      in {
        packages.${system} = {
          urbasys = pkg;
          default = pkg;
          devEnv = buildEnv { name = "devEnv"; paths = [ pyEnv ]; };
        };
        devShells.${system} = { default = devEnv; };
      });
}