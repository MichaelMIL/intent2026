# Firmware notes

| GPIO | Function | Notes |
|---|---|---|
| 0 / 1 | UART0 TX / RX | TP1 / TP2; 115200 8N1 default console |
| 4 = A (SW2, top), 3 = B (SW3), 2 = C (SW4, bottom) | keypad | active low, enable internal pull-up (`gpio_pull_up`); debounce ≥ 10 ms |
| 5–9 | D1–D5 | active high, 1 kΩ → ~1.5 mA each at 3.3 V (dim; raise brightness via PWM duty if needed, hardware can't go brighter without changing R) |
| 10 | WS2812B DIN ×4 (via U6) | PIO ws2812 program, 800 kHz, GRB order. rev 0.6: GPIO10 drives U6 (SN74LV1T34 on VSYS), so DIN swings to VSYS. LED VDD spec is 3.7–5.3 V: stop the LEDs on low battery |
| 11 | SAO2 GPIO1 (J6 pin 5) = IMU INT1 | IMU module (rev 0.6e): ST LSM6DS3TR-C on I2C0 at 0x6A (SA0 = GND); INT1 push-pull, active high by default. Input; enable a pull-down if the module may be absent |
| 22 | SAO1 GPIO1 (J5 pin 5) | IRM-H638T on the IR module: output active low, 38 kHz demodulated; enable the internal pull-up (reads high with no module) |
| 25 | SAO3 GPIO1 (J7 pin 5), also J2 pin 15 | speaker module: NPN low-side switch on an MLT-8530 transducer. Drive a 2.7 kHz square wave (PWM 50 %, or PIO); idle low. Keep the pin low/input at boot, the module has a 10 k pull-down |
| 29 | VBUS sense | ADC3; 10k/10k from VBUS -> ~2.5 V on USB, 0 V on battery |
| 12 / 13 | SAO I²C0 SDA / SCL | shared by J5–J7 and J2 pins 3/4; 4.7 kΩ pull-ups on the badge. SAO ID EEPROMs answer at 0x50 |
| 26 / 27 / 28 | SAO1/2/3 GPIO2 (pin 6) | ADC0–2; also J2 pins 16–18 |
| 14–21, 23, 24 | J2 header | free (SPI1 14/15 + 16–19, UART1 20/21) |

- BOOTSEL: hold SW1 while plugging in USB, or hold SW1 and tap SW6 RESET (rev 0.6) → UF2 mass-storage. Also reachable in firmware via `reset_usb_boot()` (e.g. hold A+B+C for 3 s) so players don't need to unplug.
- RGB current: keep brightness ≤ 25 % by default; four at full white = 144 mA from VBUS.
- Flash: W25Q16JV, 2 MB. Pico SDK `PICO_FLASH_SIZE_BYTES=2097152`, board file based on `pico.h` with `PICO_BOOT_STAGE2_CHOOSE_W25Q080 1` (same stage2 works for the JV series).
- Expansion slots (rev 0.6): three SAO 2×3 sockets (1 3V3, 2 GND, 3 SDA, 4 SCL, 5 GPIO1, 6 GPIO2). Treat each slot as its fixed function for our modules (IR = J5/GPIO22, IMU = J6/GPIO11 (INT1) + GPIO27 (INT2), I2C 0x6A, SPK = J7/GPIO25); third-party SAOs can be found by scanning I²C0 for an ID EEPROM at 0x50. A module detection trick: the IR module idles high (open-collector with pull-up) and the speaker module reads low through its 10 k; the IMU answers on I2C 0x6A (WHO_AM_I register 0x0F = 0x6A).
