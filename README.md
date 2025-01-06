# Athunas

## Wiring

A plat le wiring de la matrice ressemble à:

| Gauche | Droite |
| :----: | :----: |
|   R1   |   G1   |
|   B1   |  GND   |
|   R2   |   G2   |
|   B2   |  GND   |
|   A    |   B    |
|   C    |   D    |
|  CLK   | STROBE |
|  OE-   |  GND   |

Back Pi pinout is:

| Connection | Pin | Pin | Connection |
| ---------: | :-: | :-: | :--------- |
|          - |  2  |  1  | -          |
|          - |  4  |  3  | -          |
|    **GND** |  6  |  5  | -          |
|          - |  8  |  7  | **strobe** |
|          - | 10  |  9  | -          |
|    **OE-** | 12  | 11  | **clock**  |
|          - | 14  | 13  | **G1**     |
|      **B** | 16  | 15  | **A**      |
|      **C** | 18  | 17  | -          |
|          - | 20  | 19  | **B2**     |
|      **D** | 22  | 21  | **G2**     |
|     **R2** | 24  | 23  | **R1**     |
|     **B1** | 26  | 25  | -          |
|          - | 28  | 27  | -          |
|          - | 30  | 29  | -          |
|          - | 32  | 31  | -          |
|    **GND** | 34  | 33  | -          |
|          - | 36  | 35  | -          |
|          - | 38  | 37  | -          |
|          - | 40  | 39  | **GND**    |

Front Pi pinout is:

| Connection | Pin | Pin | Connection |
| ---------: | :-: | :-: | :--------- |
|          - |  1  |  2  | -          |
|          - |  3  |  4  | -          |
|          - |  5  |  6  | **GND**    |
| **strobe** |  7  |  8  | -          |
|          - |  9  | 10  | **E**      |
|  **clock** | 11  | 12  | **OE-**    |
|     **G1** | 13  | 14  | -          |
|      **A** | 15  | 16  | **B**      |
|          - | 17  | 18  | **C**      |
|     **B2** | 19  | 20  | -          |
|     **G2** | 21  | 22  | **D**      |
|     **R1** | 23  | 24  | **R2**     |
|          - | 25  | 26  | **B1**     |
|          - | 27  | 28  | -          |
|          - | 29  | 30  | -          |
|          - | 31  | 32  | -          |
|          - | 33  | 34  | **GND**    |
|          - | 35  | 36  | -          |
|          - | 37  | 38  | -          |
|    **GND** | 39  | 40  | -          |

After the wiring, type:

install git

```bash
sudo apt-get install git
```

install the lib:

```bash
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make -C examples-api-use
```

Launch a script:

```bash
cd examples-api-use

sudo ./demo -D 0 --led-no-hardware-pulse --led-rows=32 --led-cols=64
```

If you get any error with the display:

- Check the wiring;
- Add/remove: `--led-no-hardware-pulse`;
- Breathe in, breathe out, do it again.
