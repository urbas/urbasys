{
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "nixpkgs/nixos-unstable";

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (
      system:
      with nixpkgs.legacyPackages.${system};
      let
        pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
        pkg = python3Packages.buildPythonPackage {
          pname = pyproject.project.name;
          version = pyproject.project.version;
          src = self;
          format = "pyproject";

          propagatedBuildInputs = with python3Packages; [
            click
            dateutils
            pytimeparse
          ];

          checkInputs = with python3Packages; [
            freezegun
            pytestCheckHook
          ];

          nativeBuildInputs = with python3Packages; [
            setuptools
          ];
        };

        pkg-editable = python3.pkgs.mkPythonEditablePackage {
          pname = pyproject.project.name;
          inherit (pyproject.project) scripts version;
          root = ".";
        };
      in
      {
        packages.default = pkg;
        devShells.default = mkShell {
          packages = [
            nixfmt-rfc-style
            nodePackages.prettier
            parallel
            pkg-editable
            prek
            pyright
            ruff
            treefmt
          ];
          inputsFrom = [
            pkg
          ];
        };
      }
    );
}
