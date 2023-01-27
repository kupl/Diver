# Diver
Diver is a black-box fuzzer for SMT Solvers. The technical details of Diver can be found in our paper accepted to ICSE 2023: "Diver: Oracle-Guided SMT Solver Testing with Unrestricted Random Mutations"

# Installation

## Dependencies 
* Install Python libraries below:
```bash
pip3 install pyinterval pyparsing toml rstr termcolor numpy z3-solver cvc5
```

* Install Z3:
```bash
wget https://github.com/Z3Prover/z3/archive/refs/tags/z3-4.11.0.tar.gz
tar -xvzf z3-4.11.0.tar.gz
cd z3-z3-4.11.0
python3 scripts/mk_make.py --python
cd build
make -j 4
sudo make install
```

* Install CVC5:
```bash
wget https://github.com/cvc5/cvc5/archive/refs/tags/cvc5-1.0.1.tar.gz
tar -xvzf cvc5-1.0.1.tar.gz
cd cvc5-cvc5-1.0.1
./configure.sh --auto-download
cd build
make -j 4 
sudo make install
```

# Usage
To run Diver for testing SMT solvers, we provide instructions with example. Before executing Diver, you should prepare benchmarks and SMT solver for testing as follows:

* ``Step 1``. Please download SMT-LIB2 benchmarks from [SMT-LIB website](http://smtlib.cs.uiowa.edu/benchmarks.shtml). Diver currently can support logics associated with Boolean, Int, Reals and String.

* ``Step 2``. Download and build SMT solvers (e.g., [CVC5](https://github.com/cvc5/cvc5.git), [Z3](https://github.com/Z3Prover/z3.git) and [dReal](https://github.com/dreal/dreal4.git)) for testing with Diver. 

* ``Step 3``. You can test a SMT Solver with Diver as follows:
```bash
$ python3 __main__.py -i <seed dir> -s <solver> -b <path of binary solver file> -o <option for solver> -t <timeout for solver> -l <logic of benchmark> -m <number of mutants> -a <api for solver>
```

* ``-i`` : path of directory that stores seed formulas for testing.
* ``-s`` : name of SMT Solver for testing (e.g., z3, cvc, dreal).
* ``-b`` : path of binary SMT Solver file for testing.
* ``-o`` : option for SMT Solver.
* ``-t`` : SMT Solver timeout (per formula) in seconds (default : 10 seconds).
* ``-l`` : logic of benchmark (e.g., QF_SLIA, QF_NRA, ...).
* ``-m`` : number of mutants that will be generated (default : 1,000).
* ``-a`` : type of API SMT Solver that is recommended to set the same as ``-s``.

## ``Example``
To use Diver for testing CVC5 on ``QF_SLIA`` logic, speicfy the options as follows:
```bash
timeout TIMEOUT python3 __main__.py -i SEED_PATH -s cvc -b SOLVER_PATH -l QF_SLIA
```
Note that, in this case, ``SEED_PATH`` is path of benchmark directory, which is downloaded from [SMT-LIB website](http://smtlib.cs.uiowa.edu/benchmarks.shtml). ``SOLVER_PATH`` means path for binary file of SMT solver, which have been completed to build.

If a bug is detected, you can obtain the directory ```bug_dir```, which have subdirectories tagged with bug classes. For example, if you tested CVC5 SMT solver, the directories that has the following structure will be generated:
```text
bug_dir
├── cvc_soundness: the directory for detected soundness bugs on CVC5.
│            ├── seed1
│            |      └── seed1.smt2
│            |      └── buggy_mutant.smt2     
│            ├── seed2         
│            |      └── seed2.smt2
│            ...   
├── cvc_invalid: the directory for detected invalid-model bugs on CVC5.
│            ├── seed1 ...
|            ...  
└── cvc_crash: the directory for detected crash bugs on CVC5.
        ...
```

* The detailed options for running Diver can be cornfirmed by ```pythons __main__.py --help```.

# Implementation of Diver
Please see [STRUCTURE.md](https://github.com/kupl/Diver/blob/main/STRUCTURE.md) for implementation of Diver.

# Artifact
We provide the artifacts to reproduce the experiments in our paper: [Diver-Artifact](https://github.com/kupl/Diver-Artifact)
