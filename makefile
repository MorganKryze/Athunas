install:
	sudo apt-get install python3-tk cython3 -y

	pip install uv --break-system-packages

	@cat <<EOT >> ~/.bashrc \
	export PATH=\$${PATH}:\$${HOME}/.local/bin \
	export PYTHONPATH=\$${PYTHONPATH}:\$${HOME}/.local/lib/python3.11/site-packages \
	EOT
	@source ~/.bashrc

	sudo setcap 'cap_sys_nice=eip' /usr/bin/python3.11

build:
	make -C ./rpi-rgb-led-matrix/examples-api-use

	cd ./rpi-rgb-led-matrix/ && make build-python && cd -

	uv venv
	source .venv/bin/activate
	uv pip install .

run:
	uv run src/controller.py