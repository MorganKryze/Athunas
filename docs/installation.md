# Installation

> This is a step-by-step guide to install the project on your local machine.

- Flash the Raspberry Pi OS Lite image to your SD card using the Raspberry Pi Imager. Then boot your Raspberry Pi Zero 2W (or any other model) with the SD card.

- Connect to your machine via SSH **or** using a monitor + keyboard. Be sure to be connected to the same network.

```bash
ssh rasp@rpi.local
```

- Update your system.

```bash
sudo apt-get update -y
sudo apt-get upgrade -y
pip install --upgrade pip
```

- Install `git`.

```bash
sudo apt-get install git -y
```

- Clone the repository.

```bash
git clone --recurse-submodules https://github.com/MorganKryze/Athunas.git
```

- Change directory to the project.

```bash
cd Athunas
```

- Build the dependencies.

```bash
make -C ./rpi-rgb-led-matrix/examples-api-use
```

- If you did the wiring, you may try the demo.

```bash
sudo ./examples-api-use/demo -D 0 --led-no-hardware-pulse --led-rows=32 --led-cols=64
```

> [!TIP]
> If you get any error with the display:
>
> - Check the wiring;
> - Add/remove: `--led-no-hardware-pulse`;
> - Breathe in, breathe out, do it again.

- Install additional dependencies.

```bash
sudo apt-get install libsixel-dev python3-tk cython3 -y
```

- Install the Python dependencies and virtual environment, this may take a while.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Then install the `rpi-rgb-led-matrix` Python library.

```bash
cd rpi-rgb-led-matrix/
make build-python
make install-python
cd ..
```

- Finally, run the project.

```bash
python3 ./src/controller_v3.py
```
