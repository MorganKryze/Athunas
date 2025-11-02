# Color definitions for logging
GREEN := $(shell tput setaf 2)
BLUE := $(shell tput setaf 4)
RED := $(shell tput setaf 1)
ORANGE := $(shell tput setaf 3)
RESET := $(shell tput sgr0)

.PHONY: install
install:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Installing project python dependencies...$(RESET)"
	@pip install --break-system-packages --no-cache-dir -e . || \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to install project dependencies. Please check the logs for error.$(RESET)"; exit 1; }

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project dependencies installed successfully.$(RESET)"

.PHONY: build
build:
	@echo "[(ORANGE)  WARN   $(RESET)] $(ORANGE)Building the 'rpi-rgb-led-matrix' will take several minutes. Please be patient. Warnings can be safely ignored.$(RESET)"
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Building 'rpi-rgb-led-matrix' library api examples...$(RESET)"
	@make -C ./rpi-rgb-led-matrix/examples-api-use

	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Building 'rpi-rgb-led-matrix' Python bindings...$(RESET)"
	@make -C ./rpi-rgb-led-matrix build-python
	@sudo make -C ./rpi-rgb-led-matrix install-python
	
	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project built successfully.$(RESET)"
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)If you did the wiring, you may test the library: run 'make example' or 'make run' to run the entire project.$(RESET)"

.PHONY: example
example:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Running example demo...$(RESET)"
	@D=""; \
	while [ -z "$$D" ]; do \
		TMP=$$(shuf -i 0-11 -n 1); \
		case "$$TMP" in 1|2|3) ;; *) D=$$TMP ;; esac; \
	done; \
	sudo ./rpi-rgb-led-matrix/examples-api-use/demo -D $$D --led-rows=32 --led-cols=64 || \
		{ echo "[$(RED)  ERROR  $(RESET)] $(RED)Failed to run example demo. Please check the logs for error.$(RESET)"; exit 1; }

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Example demo completed.$(RESET)"

.PHONY: run
run:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Running project...$(RESET)"
	@sudo python src

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project stopped.$(RESET)"

.PHONY: dev
dev:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Running project with debug-level console logging...$(RESET)"
	@sudo python src --debug

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project running with debug logging.$(RESET)"

.PHONY: dev-emulator
dev-emulator:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Running project with debug-level console logging in emulator mode...$(RESET)"
	@sudo python --debug --emulator

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project running in emulator mode with debug logging.$(RESET)"

.PHONY: clean-python
clean-python:
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Cleaning up Python environment...$(RESET)"
	find src/ -name "*.pyc" -exec rm -f {} +
	find src/ -name "__pycache__" -exec rm -rf {} +

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
	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Updating project repository...$(RESET)"
	git submodule update --remote --merge
	git pull

	@echo "[$(BLUE)  INFO   $(RESET)] $(BLUE)Updating project dependencies...$(RESET)"
	@pip install --upgrade -e .

	@echo "[$(GREEN) SUCCESS $(RESET)] $(GREEN)Project and dependencies updated successfully.$(RESET)"
 