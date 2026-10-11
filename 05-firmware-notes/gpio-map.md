# Firmware notes

| GPIO | Function | Notes |
|---|---|---|
| 0 / 1 | UART0 TX / RX | TP1 / TP2; 115200 8N1 default console |
| 4 = A (SW2, top), 3 = B (SW3), 2 = C (SW4, bottom) | keypad | active low, enable internal pull-up (`gpio_pull_up`); debounce ≥ 10 ms |
| 5–9 | D1–D5 | active high, 1 kΩ → ~1.5 mA each at 3.3 V (dim; raise brightness via PWM duty if needed, hardware can't go brighter without changing R) |
| 10 | WS2812B DIN ×4 | PIO ws2812 program, 800 kHz, GRB order; LED VDD is 5 V but DIN from 3.3 V is fine on the V6 part (VIH 0.55·VDD) |
| 11 | AUDIO slot (J6 pin 3) | PWM, carrier >= 100 kHz. The audio module (R17/C21 low-pass -> C22 -> J4 tip + ring) is a breakaway board; nothing on the main board unless it is plugged in |
| 22 | IR slot (J5 pin 3) | IRM-H638T on the IR module: output active low, 38 kHz demodulated; enable the internal pull-up (reads high with no module) |
| 25 | SPK slot (J7 pin 3), also J2 pin 15 | speaker module: NPN low-side switch on an MLT-8530 transducer. Drive a 2.7 kHz square wave (PWM 50 %, or PIO); idle low. Keep the pin low/input at boot, the module has a 10 k pull-down |
| 29 | VBUS sense | ADC3; 10k/10k from VBUS -> ~2.5 V on USB, 0 V on battery |
| 12–21, 23, 24, 26–28 | J2 header | free (SPI1 12–15, I2C0 16/17, UART1 20/21, ADC0–2 26–28) |

- BOOTSEL: hold SW1 while plugging in USB → UF2 mass-storage. Also reachable in firmware via `reset_usb_boot()` (e.g. hold A+B+C for 3 s) so players don't need to unplug.
- RGB current: keep brightness ≤ 25 % by default; four at full white = 144 mA from VBUS.
- Flash: W25Q16JV, 2 MB. Pico SDK `PICO_FLASH_SIZE_BYTES=2097152`, board file based on `pico.h` with `PICO_BOOT_STAGE2_CHOOSE_W25Q080 1` (same stage2 works for the JV series).
- Expansion slots (rev 0.5): three 1×3 sockets, pin 1 = GND, 2 = 3V3, 3 = signal. A module plugged in backwards swaps GND and signal; firmware cannot tell which slot holds which module, so treat each slot as its fixed function (IR = J5/GPIO22, AUDIO = J6/GPIO11, SPK = J7/GPIO25). A module detection trick: the IR module idles high (open-collector with pull-up) and the speaker module reads low through its 10 k; the audio module is purely passive.
