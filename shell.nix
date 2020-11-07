with import <nixpkgs> {};

mkShell {
  buildInputs = [ (python27.withPackages (ps: with ps; [ numpy pygame pycairo ])) ];
}
