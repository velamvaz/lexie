#include "esp_flash.h"
#include "esp_log.h"

void lexie_print_flash_size(void)
{
    uint32_t size_mb = 0;
    if (esp_flash_get_physical_size(NULL, &size_mb) == ESP_OK) {
        size_mb /= 1024U * 1024U;
        ESP_LOGI("lexie", "Flash size: %lu MB", (unsigned long)size_mb);
    }
}
