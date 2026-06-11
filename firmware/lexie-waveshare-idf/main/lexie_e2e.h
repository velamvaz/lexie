#pragma once

#include "esp_err.h"
#include "lexie_config.h"

#define LEXIE_STRESS_WAV_PATH "/spiffs/stress_phrase.wav"

esp_err_t lexie_e2e_load_stress_wav(uint8_t **wav_out, size_t *wav_len);
void lexie_e2e_free_stress_wav(uint8_t *wav);

esp_err_t lexie_e2e_cycle(const lexie_config_t *cfg,
                          const uint8_t *wav,
                          size_t wav_len,
                          int cycle_n,
                          int cycle_total);

void lexie_stress_run(const lexie_config_t *cfg, int cycles);
