#pragma once

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"

#define LEXIE_MAX_NETWORKS 3
#define LEXIE_SSID_MAX 32
#define LEXIE_PASS_MAX 64
#define LEXIE_URL_MAX 128
#define LEXIE_KEY_MAX 128

typedef struct {
    char ssid[LEXIE_SSID_MAX];
    char password[LEXIE_PASS_MAX];
} lexie_network_t;

typedef struct {
    lexie_network_t networks[LEXIE_MAX_NETWORKS];
    size_t network_count;
    char base_url[LEXIE_URL_MAX];
    char device_key[LEXIE_KEY_MAX];
} lexie_config_t;

esp_err_t lexie_config_load(lexie_config_t *out);
