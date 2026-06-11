#pragma once

#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
#include "lexie_config.h"

esp_err_t lexie_http_health(const lexie_config_t *cfg);

typedef struct {
    uint8_t *data;
    size_t len;
} lexie_http_body_t;

esp_err_t lexie_http_explain(const lexie_config_t *cfg,
                             const uint8_t *wav,
                             size_t wav_len,
                             lexie_http_body_t *out_mp3);

void lexie_http_body_free(lexie_http_body_t *body);
