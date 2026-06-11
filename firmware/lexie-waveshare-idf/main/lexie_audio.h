#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"

#define LEXIE_SAMPLE_RATE 16000
#define LEXIE_RECORD_MAX_SEC 10
#define LEXIE_RECORD_MIN_MS 500

esp_err_t lexie_spiffs_init(void);
esp_err_t lexie_board_audio_init(void);
esp_err_t lexie_record_ptt(int boot_gpio, uint8_t **wav_out, size_t *wav_len);
esp_err_t lexie_play_mp3_bytes(const uint8_t *data, size_t len);
void lexie_play_error_beep(void);
void lexie_set_pipeline_busy(bool busy);
bool lexie_pipeline_is_busy(void);
void lexie_audio_player_drain(void);
