#pragma once

#include "lexie_config.h"
#include "esp_err.h"

esp_err_t lexie_wifi_connect(const lexie_config_t *cfg);
esp_err_t lexie_wifi_ensure_connected(const lexie_config_t *cfg);
