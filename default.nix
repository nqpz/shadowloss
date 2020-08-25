with import <nixpkgs> {};
stdenv.mkDerivation {
    name = "shadowloss";
    buildInputs = [ (python27.withPackages (ps: with ps; [ numpy pygame pycairo ])) ];
}
