# Waveshare ESP32-S3-AUDIO-Board reference (partial)

Vendored **driver subset** from [Waveshare esp32-s3-audio-board-starter](https://www.waveshare.com/wiki/ESP32-S3-AUDIO-Board) for Lexie ESP-IDF firmware.

Only these paths are tracked (used by `firmware/lexie-waveshare-idf`):

- `esp32-s3-audio-board-starter/main/Audio_Driver/`
- `esp32-s3-audio-board-starter/main/I2C_Driver/`
- `esp32-s3-audio-board-starter/main/I2S_Driver/`
- `esp32-s3-audio-board-starter/main/EXIO/`

Full upstream demo (LVGL, camera, etc.) is not in git. Use `tools/wx036-clone-demo.sh` locally if needed.
