NAME = a_maze_ing.py

PYTHON = python3
PIP = pip

GREEN = \033[0;32m
RESET = \033[0m

all: run

install:
	@echo "$(GREEN)Installation des dépendances...$(RESET)"
	$(PIP) install flake8 mypy pytest

run:
	$(PYTHON) $(NAME) config.txt

debug:
	$(PYTHON) -m pdb $(NAME) config.txt

build:
	@echo "$(GREEN)Construction du package mazegen...$(RESET)"
	$(PIP) install --quiet build
	$(PYTHON) -m build
	mv dist/*.whl dist/*.tar.gz .
	rm -rf dist build mazegen.egg-info
	@echo "$(GREEN)Package disponible à la racine.$(RESET)"

clean:
	@echo "$(GREEN)Nettoyage complet...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf build dist *.egg-info mazegen.egg-info
	find . -name "mazegen-*.whl" -delete
	find . -name "mazegen-*.tar.gz" -delete
	find . -type f -name "*.pyc" -deletelint:
	@echo "$(GREEN)Vérification flake8...$(RESET)"
	flake8 .
	@echo "$(GREEN)Vérification mypy...$(RESET)"
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		 --disallow-untyped-defs --check-untyped-defs .

.PHONY: all install run debug clean lint build