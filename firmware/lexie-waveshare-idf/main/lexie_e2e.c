#include "lexie_e2e.h"

#include "lexie_audio.h"
#include "lexie_http.h"
#include "lexie_wifi.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "lexie_e2e";

static uint32_t heap_psram_free(void)
{
    return (uint32_t)heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
}

static uint32_t now_ms(void)
{
    return (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);
}

esp_err_t lexie_e2e_load_stress_wav(uint8_t **wav_out, size_t *wav_len)
{
    FILE *f = fopen(LEXIE_STRESS_WAV_PATH, "rb");
    if (!f) {
        ESP_LOGE(TAG, "Missing %s — run wx033-provision-idf.sh", LEXIE_STRESS_WAV_PATH);
        return ESP_FAIL;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return ESP_FAIL;
    }
    long sz = ftell(f);
    if (sz <= 44 || sz > 256 * 1024) {
        ESP_LOGE(TAG, "stress WAV size invalid: %ld", sz);
        fclose(f);
        return ESP_FAIL;
    }
    rewind(f);

    uint8_t *buf = heap_caps_malloc((size_t)sz, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (!buf) {
        buf = malloc((size_t)sz);
    }
    if (!buf) {
        fclose(f);
        return ESP_ERR_NO_MEM;
    }
    if (fread(buf, 1, (size_t)sz, f) != (size_t)sz) {
        free(buf);
        fclose(f);
        return ESP_FAIL;
    }
    fclose(f);

    *wav_out = buf;
    *wav_len = (size_t)sz;
    ESP_LOGI(TAG, "Loaded stress WAV %u bytes", (unsigned)*wav_len);
    return ESP_OK;
}

void lexie_e2e_free_stress_wav(uint8_t *wav)
{
    free(wav);
}

static esp_err_t explain_with_retry(const lexie_config_t *cfg,
                                    const uint8_t *wav,
                                    size_t wav_len,
                                    lexie_http_body_t *mp3,
                                    uint32_t *elapsed_ms)
{
    const int max_attempts = 3;
    uint32_t t0 = now_ms();

    for (int attempt = 0; attempt < max_attempts; attempt++) {
        if (attempt > 0) {
            ESP_LOGW(TAG, "explain retry %d/%d", attempt + 1, max_attempts);
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
        esp_err_t err = lexie_http_explain(cfg, wav, wav_len, mp3);
        if (err == ESP_OK) {
            if (elapsed_ms) {
                *elapsed_ms = (uint32_t)(now_ms() - t0);
            }
            return ESP_OK;
        }
    }
    if (elapsed_ms) {
        *elapsed_ms = (uint32_t)(now_ms() - t0);
    }
    return ESP_FAIL;
}

static esp_err_t playback_with_retry(const uint8_t *data, size_t len, uint32_t *elapsed_ms)
{
    const int max_attempts = 3;
    uint32_t t0 = now_ms();

    for (int attempt = 0; attempt < max_attempts; attempt++) {
        if (attempt > 0) {
            ESP_LOGW(TAG, "playback retry %d/%d", attempt + 1, max_attempts);
            lexie_audio_player_drain();
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
        esp_err_t err = lexie_play_mp3_bytes(data, len);
        if (err == ESP_OK) {
            if (elapsed_ms) {
                *elapsed_ms = (uint32_t)(now_ms() - t0);
            }
            return ESP_OK;
        }
    }
    if (elapsed_ms) {
        *elapsed_ms = (uint32_t)(now_ms() - t0);
    }
    return ESP_FAIL;
}

esp_err_t lexie_e2e_cycle(const lexie_config_t *cfg,
                          const uint8_t *wav,
                          size_t wav_len,
                          int cycle_n,
                          int cycle_total)
{
    lexie_set_pipeline_busy(true);

    if (lexie_wifi_ensure_connected(cfg) != ESP_OK) {
        ESP_LOGE(TAG, "LEXIE_E2E: cycle=%d/%d FAIL stage=wifi err=disconnected heap=%u",
                 cycle_n, cycle_total, (unsigned)heap_psram_free());
        lexie_set_pipeline_busy(false);
        return ESP_FAIL;
    }
    ESP_LOGI(TAG, "LEXIE_E2E: cycle=%d/%d stage=wifi_ok", cycle_n, cycle_total);

    lexie_http_body_t mp3 = {0};
    uint32_t explain_ms = 0;
    esp_err_t http = explain_with_retry(cfg, wav, wav_len, &mp3, &explain_ms);
    if (http != ESP_OK) {
        ESP_LOGE(TAG, "LEXIE_E2E: cycle=%d/%d FAIL stage=explain err=http heap=%u",
                 cycle_n, cycle_total, (unsigned)heap_psram_free());
        lexie_set_pipeline_busy(false);
        return ESP_FAIL;
    }
    ESP_LOGI(TAG, "LEXIE_E2E: cycle=%d/%d stage=explain_ok bytes=%u ms=%u",
             cycle_n, cycle_total, (unsigned)mp3.len, (unsigned)explain_ms);

    uint32_t playback_ms = 0;
    esp_err_t play = playback_with_retry(mp3.data, mp3.len, &playback_ms);
    lexie_http_body_free(&mp3);

    if (play != ESP_OK) {
        ESP_LOGE(TAG, "LEXIE_E2E: cycle=%d/%d FAIL stage=playback err=decode heap=%u",
                 cycle_n, cycle_total, (unsigned)heap_psram_free());
        lexie_set_pipeline_busy(false);
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "LEXIE_E2E: cycle=%d/%d stage=playback_ok ms=%u",
             cycle_n, cycle_total, (unsigned)playback_ms);
    lexie_set_pipeline_busy(false);
    return ESP_OK;
}

void lexie_stress_run(const lexie_config_t *cfg, int cycles)
{
    uint8_t *wav = NULL;
    size_t wav_len = 0;
    if (lexie_e2e_load_stress_wav(&wav, &wav_len) != ESP_OK) {
        lexie_play_error_beep();
        return;
    }

    ESP_LOGI(TAG, "LEXIE_E2E: starting stress test cycles=%d", cycles);

    int pass = 0;
    int fail = 0;
    for (int i = 1; i <= cycles; i++) {
        if (lexie_e2e_cycle(cfg, wav, wav_len, i, cycles) == ESP_OK) {
            pass++;
        } else {
            fail++;
        }
        if (i < cycles) {
            vTaskDelay(pdMS_TO_TICKS(4000));
        }
    }

    lexie_e2e_free_stress_wav(wav);
    ESP_LOGI(TAG, "LEXIE_E2E: SUMMARY pass=%d fail=%d", pass, fail);

    if (fail == 0) {
        ESP_LOGI(TAG, "Stress test PASSED (%d/%d)", pass, cycles);
    } else {
        ESP_LOGE(TAG, "Stress test FAILED pass=%d fail=%d", pass, fail);
        lexie_play_error_beep();
    }
}
