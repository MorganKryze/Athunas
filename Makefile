# Color definitions for logging
GREEN := $(shell tput setaf 2)
BLUE := $(shell tput setaf 4)
RED := $(shell tput setaf 1)
ORANGE := $(shell tput setaf 3)
RESET := $(shell tput sgr0)

.PHONY: install
install:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Installing system dependencies...$(RESET)"
	@sudo apt-get install libsixel-dev python3-tk cython3 python3-pip -y ||  \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to install system dependencies. Please check the logs for error.$(RESET)"; exit 1; }
	
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Adding 'cap_sys_nice' capability to 'python3.11'...$(RESET)"
	@sudo setcap 'cap_sys_nice=eip' /usr/bin/python3.11 || \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to set capabilities. Please check the logs for error.$(RESET)"; exit 1; }
	
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Installing 'uv' (you may ignore their recommendation)...$(RESET)"
	@curl -LsSf https://astral.sh/uv/install.sh | sh || \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to install 'uv'. Please check the logs for error.$(RESET)"; exit 1; }
	
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Adding 'uv' to PATH...$(RESET)"
	@echo "export PATH=\$${PATH}:\$${HOME}/.local/bin" >> ~/.bashrc || \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to update PATH. Please check the logs for error.$(RESET)"; exit 1; }

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)System dependencies installed successfully.$(RESET)"

.PHONY: build
build:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Creating python virtual environment...$(RESET)"
	@export PATH=$$PATH:$$HOME/.local/bin || \
		{ echo "[$(ORANGE)  WARNING  $(RESET)] $(ORANGE)Failed to source binaries directory. Please run 'source ~/.bashrc' manually.$(RESET)"; }
	@uv venv || \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to create virtual environment. Please check the logs for error.$(RESET)"; exit 1; }

	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Installing project python dependencies...$(RESET)"
	@uv pip install || \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to install project dependencies. Please check the logs for error.$(RESET)"; exit 1; }

	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Building 'rpi-rgb-led-matrix' library...$(RESET)"
	@make -C ./rpi-rgb-led-matrix/examples-api-use
	@make -C ./rpi-rgb-led-matrix build-python
	
	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project built successfully.$(RESET)"
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)To test the library, run 'make example' or 'make run' to run the project.$(RESET)"

.PHONY: example
example:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Running example demo...$(RESET)"
	@sudo ./rpi-rgb-led-matrix/examples-api-use/demo -D 0 --led-no-hardware-pulse --led-rows=32 --led-cols=64 || \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to run example demo. Please check the logs for error.$(RESET)"; exit 1; }

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Example demo completed.$(RESET)"

.PHONY: run
run:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Running project...$(RESET)"
	@uv run src

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project stopped.$(RESET)"

.PHONY: dev
dev:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Running project with debug-level console logging...$(RESET)"
	@uv run src --debug

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project running with debug logging.$(RESET)"

.PHONY: dev-emulator
dev-emulator:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Running project with debug-level console logging in emulator mode...$(RESET)"
	@uv run src --debug --emulator

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project running in emulator mode with debug logging.$(RESET)"

.PHONY: clean-python
clean-python:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Cleaning up Python environment...$(RESET)"
	find . -name "*.pyc" -exec rm -f {} +
	find . -name "__pycache__" -exec rm -rf {} +
	rm -rf .venv
	rm -rf build
	rm -rf src/*.egg-info

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Python environment cleaned up.$(RESET)"

.PHONY: clean-library
clean-library:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Cleaning up 'rpi-rgb-led-matrix' build artifacts...$(RESET)"
	@make -C ./rpi-rgb-led-matrix/examples-api-use clean
	@make -C ./rpi-rgb-led-matrix clean

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)'rpi-rgb-led-matrix' build artifacts cleaned up.$(RESET)"

.PHONY: clean
clean: clean-python clean-library
	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)All clean operations completed successfully.$(RESET)"

.PHONY: update
update:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Updating 'uv'...$(RESET)"
	uv self update || \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to update 'uv'. Please check the logs for error.$(RESET)"; exit 1; }

	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Updating project repository...$(RESET)"
	git submodule update --remote --merge
	git pull

	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Updating project dependencies...$(RESET)"
	uv pip install --upgrade .

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project and dependencies updated successfully.$(RESET)"
 