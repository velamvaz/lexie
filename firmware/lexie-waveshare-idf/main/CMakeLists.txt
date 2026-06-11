set(STARTER_MAIN "${CMAKE_CURRENT_SOURCE_DIR}/../../wx036-reference/esp32-s3-audio-board-starter/main")

set(SOURCES
    "main.c"
    "lexie_config.c"
    "lexie_wifi.c"
    "lexie_http.c"
    "lexie_audio.c"
    "lexie_audio_mp3_bridge.cpp"
    "lexie_e2e.c"
    "lexie_flash.c"
    "board/SD_MMC_stub.c"
    "board/Button_Driver_stub.c"
    "board/i2s_board.c"
    "${STARTER_MAIN}/EXIO/TCA9555PWR.c"
    "${STARTER_MAIN}/Audio_Driver/Audio_Driver.c"
    "${STARTER_MAIN}/I2C_Driver/I2C_Driver.c"
)

set(INCLUDE_DIRS
    "."
    "board"
    "${CMAKE_CURRENT_SOURCE_DIR}/../managed_components/chmorgan__esp-audio-player"
    "${STARTER_MAIN}/Audio_Driver"
    "${STARTER_MAIN}/EXIO"
    "${STARTER_MAIN}/I2C_Driver"
    "${STARTER_MAIN}/I2S_Driver"
)

idf_component_register(
    SRCS ${SOURCES}
    INCLUDE_DIRS ${INCLUDE_DIRS}
    REQUIRES json esp_wifi esp_netif esp_http_client esp_event nvs_flash spiffs mbedtls esp_codec_dev chmorgan__esp-audio-player driver unity esp_driver_i2c esp_driver_i2s spi_flash
)
