# Implementation of Diver
We implemented Diver in Python code. The detailed structure and main python file for Diver is as follows:

```text
Diver
├── __main__.py 
├── analyzer: 
│         ├── pre_analyzer.py 
│         ...      
│         └── ...    
├── fuzzer: 
│       ├── generator.py
|       └── evaluator.py
├── parser: 
│        └── smt_parser.py
└── utils: 
      ├── ...
      ...
      └── ... 
```
In our paper "Diver: Oracle-Guided SMT Solver Testing with Unrestricted Random Mutations" accepted in ICSE 2023, the Algorithm 1,2 and 3 in our paper was developed as follows:

* The Algorithm 1 (Diver Algorithm) developed in ```__main__.py```
* The Algorithm 2 (The procedure Pre-Analysis) was implemented in ```analyzer/pre_analzyer.py```. We developed our analyzer, which generates the constraints for functions in each logic such as boolean, integer, real and string, on top of the py inteval library and re module.
* The Algorithm 3 (The procedure GenMutant) was implemented in ```fuzzer/generator.py```. The ```fuzzer/evaluator.py``` checked if a mutant formula generated by ```fuzzer/generator.py```  is satisfiable by the model of seed formula. We made ```fuzzer/generator.py``` using CVC5 and Z3 python libraries.
