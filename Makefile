SHELL := /bin/bash
CC ?= cc
CFLAGS = -Wall -Wextra -Werror
PY ?= python3
.PHONY: all popen pico picoshell vbc clean help exam exam-start exam-test exam-push

all: popen pico vbc

popen:
	@set -euo pipefail; \
	cd ft_popen; \
	$(CC) -Wall -Wextra -Werror -O2 ft_popen.c test_ft_popen.c -o test_ft_popen; \
	./test_ft_popen

pico: picoshell
picoshell:
	@set -euo pipefail; \
	cd picoshell; \
	$(CC) -Wall -Wextra -Werror -O2 picoshell.c test_picoshell.c -o test_picoshell; \
	./test_picoshell

vbc:
	@set -euo pipefail; \
	cd vbc; \
	$(CC) $(CFLAGS) -O2 vbc.c -o vbc; \
	RST="\033[0m"; BOLD="\033[1m"; GRN="\033[32m"; RED="\033[31m"; CYN="\033[36m"; \
	print_result() { if [[ $$2 -eq 1 ]]; then printf "  %s[PASS]%s %s\n" "$$GRN" "$$RST" "$$1"; else printf "  %s[FAIL]%s %s\n" "$$RED" "$$RST" "$$1"; fi; }; \
	pass=0; total=0; \
	printf "\n%s[vbc Tests]%s %s(many cases)%s\n" "$$BOLD" "$$RST" "$$CYN" "$$RST"; \
	test_case() { total=$$((total+1)); expr="$$1"; expect="$$2"; set +e; out=$$(./vbc "$$expr" 2>&1); code=$$?; set -e; \
	  if [[ "$$expect" =~ ^ERR: ]]; then want_msg=$${expect#ERR:}; \
	    if [[ $$code -ne 0 && "$$out" == "$$want_msg" ]]; then pass=$$((pass+1)); print_result "$$expr" 1; else print_result "$$expr" 0; fi; \
	  else if [[ $$code -eq 0 && "$$out" == "$$expect" ]]; then pass=$$((pass+1)); print_result "$$expr = $$expect" 1; else print_result "$$expr = $$expect" 0; fi; fi; \
	}; \
	test_case '1' '1'; \
	test_case '2+3' '5'; \
	test_case '3*4+5' '17'; \
	test_case '3+4*5' '23'; \
	test_case '(3+4)*5' '35'; \
	test_case '(((((2+2)*2+2)*2+2)*2+2)*2+2)*2' '188'; \
	test_case '1+2+3+4+5' '15'; \
	test_case '(1)' '1'; \
	test_case '(((((((3)))))))' '3'; \
	test_case '(1+2)*3' '9'; \
	test_case '2*4+9+3+2*1+5+1+6+6*1*1+8*0+0+5+0*4*9*5*8+9*7+5*1+3+1+4*5*7*3+0*3+4*8+8+8+4*0*5*3+5+4+5*7+9+6*6+7+9*2*6*9+2+1*3*7*1*1*5+1+2+7+4+3*4*2+0+4*4*2*2+6+7*5+9+0+8*4+6*7+5+4*4+2+5*5+1+6+3*5*9*9+7*4*3+7+4*9+3+0+1*8+1+2*9*4*5*1+0*1*9+5*3*5+9*6+5*4+5+5*8*6*4*9*2+0+0+1*5*3+6*8*0+0+2*3+7*5*6+8+6*6+9+3+7+0*0+5+2*8+2*7*2+3+9*1*4*8*7*9+2*0+1*6*4*2+8*8*3*1+8+2*4+8*3+8*3+9*5+2*3+9*5*6*4+3*6*6+7+4*8+0+2+9*8*0*6*8*1*2*7+0*5+6*5+0*2+7+2+3+8*7+6+1*3+5+4*5*4*6*1+4*7+9*0+4+9*8+7+5+6+2+6+1+1+1*6*0*9+7+6*2+4*4+1*6*2*9+3+0+0*1*8+4+6*2+6+2*7+7+0*9+6+2*1+6*5*2*3*5*2*6*4+2*9*2*4*5*2*2*3+8+8*3*2*3+0*5+9*6+8+3*1+6*9+8+9*2*0+2' '94305'; \
	test_case '1+' 'ERR:Unexpected end of input'; \
	test_case '1+2)' "ERR:Unexpected token ')'"; \
	test_case '((1+3)*12+(3*(2+6))' "ERR:Unexpected token '2'"; \
	if [[ $$pass -eq $$total ]]; then printf "%sAll tests passed%s (%d/%d)\n" "$$GRN" "$$RST" "$$pass" "$$total"; else printf "%sSome tests failed%s (%d/%d)\n" "$$RED" "$$RST" "$$pass" "$$total"; fi; \
	exit $$([[ $$pass -eq $$total ]] && echo 0 || echo 1)

# Examshell (mini_exam04.py) targets
exam: exam-start

exam-start:
	@$(PY) mini_exam04.py start

exam-test:
	@if [ -z "$(ASSIGNMENT)" ]; then echo "ASSIGNMENT is required. Usage: make exam-test ASSIGNMENT={ft_popen|picoshell|vbc} [FILE=path/to/file.c]"; exit 1; fi; \
	if [ -n "$(FILE)" ]; then $(PY) mini_exam04.py test "$(ASSIGNMENT)" "$(FILE)"; else $(PY) mini_exam04.py test "$(ASSIGNMENT)"; fi

exam-push:
	@if [ -z "$(ASSIGNMENT)" ]; then echo "ASSIGNMENT is required. Usage: make exam-push ASSIGNMENT={ft_popen|picoshell|vbc}"; exit 1; fi; \
	$(PY) mini_exam04.py push "$(ASSIGNMENT)"

clean:
	@rm -f ./ft_popen/test_ft_popen ./picoshell/test_picoshell ./vbc/vbc \
		./ft_popen/.tmp_out ./picoshell/.pico_out ./picoshell/.pico_out2 \
		./ft_popen/tester.sh ./picoshell/tester.sh ./vbc/tester.sh
	@echo "Cleaned build artifacts"

help:
	@echo "Targets:";
	@echo "  make popen     - build/run ft_popen tests";
	@echo "  make pico      - build/run picoshell tests";
	@echo "  make vbc       - build/run vbc tests";
	@echo "  make all       - run all tests";
	@echo "  make exam      - start interactive examshell (mini_exam04.py)";
	@echo "  make exam-test ASSIGNMENT=... [FILE=...] - run examshell in test mode";
	@echo "  make exam-push ASSIGNMENT=... - archive from rendu and re-test";
	@echo "  make clean     - clean artifacts";
