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
          freezegun
          pytestCheckHook
        ];

        propagatedBuildInputs = with python3Packages; [
          click
          dateutils
          pytimeparse
        ];

        devInputs = with python3Packages; [
          black
          flake8
          mypy
          pytest
          pytest-cov
          pytest-watch
          types-dateutil
        ];

        pyEnv = python3.withPackages(_: checkInputs ++ devInputs ++ propagatedBuildInputs);
        nixpkgs-cache = pkgs.runCommand "nixpkgs" { } "mkdir $out && ln -s ${nixpkgs} $out/$(basename ${nixpkgs})";
        devEnv = [ pyEnv nixpkgs-cache ];

        pkg = python3Packages.buildPythonApplication {
          pname = "urbasys";
          version = "local";
          src = lib.cleanSourceWith { src = ./.; };
          inherit checkInputs propagatedBuildInputs;
        };

      in {
        packages.${system} = {
          urbasys = pkg;
          default = pkg;
          devEnv = buildEnv { name = "devEnv"; paths = devEnv; };
        };
        devShells.${system} = { default = pkg.overrideAttrs(oldAttrs: { nativeBuildInputs = oldAttrs.nativeBuildInputs ++ devInputs; }); };
      });
}
