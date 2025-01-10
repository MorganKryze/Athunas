COMMANDS=install build run

all: $(COMMANDS)

install:
# Install dependencies to build 'rpi-rgb-led-matrix'
	sudo apt-get install python3-tk cython3 -y
# Install 'uv' using 'pip'
	pip install uv --break-system-packages
# Add 'uv' to PATH and PYTHONPATH
	echo "export PATH=\$${PATH}:\$${HOME}/.local/bin" >> ~/.bashrc
	echo "export PYTHONPATH=\$${PYTHONPATH}:\$${HOME}/.local/lib/python3.11/site-packages" >> ~/.bashrc
	. ~/.bashrc
# Allow 'python3.11' to use 'cap_sys_nice'
	sudo setcap 'cap_sys_nice=eip' /usr/bin/python3.11

build:
# Build 'rpi-rgb-led-matrix' examples
	make -C ./rpi-rgb-led-matrix/examples-api-use
# Build 'rpi-rgb-led-matrix' python bindings
	make -C ./rpi-rgb-led-matrix build-python
# Setup virtual environment
	uv venv
# Enter virtual environment
	. .venv/bin/activate
# Install project python dependencies
	uv pip install .

example:
# Run 'rpi-rgb-led-matrix' default example
	sudo ./rpi-rgb-led-matrix/examples-api-use/demo -D 0 --led-no-hardware-pulse --led-rows=32 --led-cols=64

run:
# Run project controller
	uv run src/controller.py

clean:
# Clean virtual environment
	rm -rf .venv
	rm -rf build
	rm -rf src/*.egg-info
	rm -rf src/__pycache__
# Clean built dependencies
	make -C ./rpi-rgb-led-matrix/examples-api-use clean
	make -C ./rpi-rgb-led-matrix clean

update:
# Update 'uv' package
	pip install --upgrade uv
# Pull latest changes from 'rpi-rgb-led-matrix' repository
	git submodule update --remote --merge
# pulling the latest changes from project repository
	git pull
# Update project dependencies
	uv pip install --upgrade .
