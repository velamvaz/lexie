#include "lexie_config.h"
#include "lexie_http.h"
#include "lexie_audio.h"
#include "lexie_wifi.h"

#include "lexie_flash.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

#if CONFIG_LEXIE_STRESS_TEST
#include "lexie_e2e.h"
#endif

#define LEXIE_PTT_GPIO GPIO_NUM_0

static const char *TAG = "lexie";

static void lexie_ptt_loop(const lexie_config_t *cfg)
{
    ESP_LOGI(TAG, "Ready — hold BOOT, speak a word, release");

    while (1) {
        uint8_t *wav = NULL;
        size_t wav_len = 0;
        esp_err_t rec = lexie_record_ptt(LEXIE_PTT_GPIO, &wav, &wav_len);
        if (rec != ESP_OK) {
            if (rec != ESP_ERR_INVALID_SIZE && rec != ESP_ERR_INVALID_STATE) {
                lexie_play_error_beep();
            }
            vTaskDelay(pdMS_TO_TICKS(200));
            continue;
        }

        lexie_set_pipeline_busy(true);
        lexie_http_body_t mp3 = {0};
        esp_err_t http = lexie_http_explain(cfg, wav, wav_len, &mp3);
        free(wav);

        if (http != ESP_OK) {
            lexie_set_pipeline_busy(false);
            lexie_play_error_beep();
            continue;
        }

        if (lexie_play_mp3_bytes(mp3.data, mp3.len) != ESP_OK) {
            lexie_play_error_beep();
        }
        lexie_http_body_free(&mp3);
        lexie_set_pipeline_busy(false);
    }
}

static void lexie_run(void *arg)
{
    (void)arg;
    lexie_config_t cfg;
    if (lexie_config_load(&cfg) != ESP_OK) {
        ESP_LOGE(TAG, "Config load failed");
        vTaskDelete(NULL);
        return;
    }

    if (lexie_wifi_connect(&cfg) != ESP_OK) {
        ESP_LOGE(TAG, "Wi-Fi failed");
        lexie_play_error_beep();
        vTaskDelete(NULL);
        return;
    }

    if (lexie_http_health(&cfg) != ESP_OK) {
        ESP_LOGE(TAG, "Health check failed");
        lexie_play_error_beep();
        vTaskDelete(NULL);
        return;
    }

#if CONFIG_LEXIE_STRESS_TEST
    ESP_LOGI(TAG, "Stress test mode (%d cycles)", CONFIG_LEXIE_STRESS_CYCLES);
    lexie_stress_run(&cfg, CONFIG_LEXIE_STRESS_CYCLES);
    vTaskDelay(portMAX_DELAY);
#else
    lexie_ptt_loop(&cfg);
#endif
}

void app_main(void)
{
    gpio_reset_pin(LEXIE_PTT_GPIO);
    gpio_set_direction(LEXIE_PTT_GPIO, GPIO_MODE_INPUT);
    gpio_set_pull_mode(LEXIE_PTT_GPIO, GPIO_PULLUP_ONLY);

    lexie_print_flash_size();
    ESP_ERROR_CHECK(lexie_spiffs_init());
    ESP_ERROR_CHECK(lexie_board_audio_init());

    xTaskCreatePinnedToCore(lexie_run, "lexie_run", 12288, NULL, 5, NULL, 1);
}
