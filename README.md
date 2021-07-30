# CoAPI for computing MCSs and prime compilation

An implementation of CoAPI is published in ICCAD21[1].

[1] Weilin Luo, Hai Wan, Hongzhen Zhong, Ou Wei, Biqing Fang and Xiaotong Song. "An Efficient Two-Phase Method for Prime Compilation of Non-Clausal Boolean Formulae," in Proceedings of International Conference on Computer Aided Design (ICCAD), 2021.

---
## Compile and Run

- change to the directory ./
	```
	$ python2 Main.py -cc='CompileCover' -ac='CompileAll' -bm='test' -lt=3600 -pin=1 -uca=1
	```

- cc	: select the CompileCover solver
- ac	: select the CompileAll solver
- bm	: select the benchmarks
- lt	: set the limit time
- pin	: set the computation of prime implicates or implicants (0: prime implicates; 1: prime implicants)
- uca	: set the extracting method to BPE

---
## Output

- If you want to check all primes of the instance ${f} in the benchmark ${Benchmark}, you can see the ./example/${Benchmark}/${f}.out file.
- If you want to check the overview of the instance ${f} in the benchmark ${Benchmark}, you can see the ./example/output/${Benchmark}/${f}.res file.

---
## Directory Overview

- ./example: Benchmarks
- ./Solver : CompileCover and CompileAll solver

---
## Configuration

- [Ubuntu 18]
- [python 2.7]

---
## Note

- If there is an error "Memory out" immediately, place check that the perissions of the ./Solver/CompileCover and ./Solver/CompileAll are "Allow executing file as program".

---
## The framework of CoAPI

"f-p.cnf"                  "f.cpi"        "f.cnf"        	"f.out"
		  -> |CompileCover|  ->  |cpi2cnf|  ->  |CompileAll|  ->  |output| -> "f.res"
"f-n.cnf"

f is a formula 
- "f-p.cnf": f in CNF with unsigned normal encoding
- "f-n.cnf": negative f in CNF with unsigned normal encoding
- "f.cpi"  : the succinct cover of negative f with signed normal encoding
- "f.cnf"  : the succinct cover of f with unsigned dual rail encoding
- "f.out"  : all the prime implicants of f with unsigned normal encoding
- "f.res"  : output file. It will be show in ./example/output/${Benchmark}/

---
## Encoding of CoAPI

For a variable $x$, encoded by x = 1, we encode its literals $x$ and $\lnot x$ with following:
- unsigned normal encoding: $x$ -> 1 (x); $\lnot x$ -> -1 (-x)
- signed normal encoding: $x$ -> 2 (x * 2); $\lnot x$ -> 3 (x * 2 + 1)
- unsigned dual rail encoding: $x$ -> 2 (x * 2); $\lnot x$ -> 1 (x * 2 - 1)
