#include "lexie_audio.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "Audio_Driver.h"
#include "I2C_Driver.h"
#include "I2S_Driver.h"
#include "TCA9555PWR.h"
#include "esp_codec_dev.h"
#include "lexie_audio_mp3_bridge.h"
#include "driver/gpio.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_spiffs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "mp3dec.h"

static const char *TAG = "lexie_audio";
static const char *SPIFFS_MOUNT = "/spiffs";
#define LEXIE_PTT_ACTIVE 0

static volatile bool s_pipeline_busy;

typedef struct {
    HMP3Decoder decoder;
    mp3_instance mp3_data;
    decode_data output;
    bool ready;
} lexie_mp3_direct_t;

static lexie_mp3_direct_t s_mp3_direct;

typedef struct __attribute__((packed)) {
    char riff[4];
    uint32_t chunk_size;
    char wave[4];
    char fmt[4];
    uint32_t fmt_size;
    uint16_t audio_format;
    uint16_t num_channels;
    uint32_t sample_rate;
    uint32_t byte_rate;
    uint16_t block_align;
    uint16_t bits_per_sample;
    char data[4];
    uint32_t data_size;
} wav_header_t;

static void lexie_pa_enable(bool on)
{
    Set_EXIO(IO_EXPANDER_PIN_NUM_8, on);
    vTaskDelay(pdMS_TO_TICKS(50));
}

static esp_err_t bsp_i2s_write(void *audio_buffer, size_t len, size_t *bytes_written, uint32_t timeout_ms)
{
    (void)timeout_ms;
    size_t sample_count = len / sizeof(uint8_t);
    int ret = esp_codec_dev_write(output_dev, audio_buffer, (int)sample_count);
    if (ret != ESP_CODEC_DEV_OK) {
        ESP_LOGE(TAG, "codec write failed ret=%d len=%u", ret, (unsigned)sample_count);
        return ESP_FAIL;
    }
    if (bytes_written) {
        *bytes_written = sample_count;
    }
    return ESP_OK;
}

static esp_err_t lexie_output_set_format(uint32_t rate, uint32_t channels, uint32_t bits)
{
    esp_codec_dev_close(output_dev);
    esp_codec_dev_sample_info_t fs = {
        .sample_rate = rate,
        .channel = channels,
        .bits_per_sample = bits,
    };
    int ret = esp_codec_dev_open(output_dev, &fs);
    if (ret != ESP_CODEC_DEV_OK) {
        ESP_LOGE(TAG, "codec open failed sr=%u ch=%u bits=%u ret=%d", (unsigned)rate,
                 (unsigned)channels, (unsigned)bits, ret);
        return ESP_FAIL;
    }
    esp_codec_dev_set_out_vol(output_dev, (int)Volume);
    lexie_pa_enable(true);
    return ESP_OK;
}

static void lexie_mp3_reset_decoder(void)
{
    if (s_mp3_direct.decoder) {
        MP3FreeDecoder(s_mp3_direct.decoder);
        s_mp3_direct.decoder = NULL;
    }
    s_mp3_direct.decoder = MP3InitDecoder();
}

static esp_err_t lexie_mp3_direct_init(void)
{
    if (s_mp3_direct.ready) {
        return ESP_OK;
    }
    s_mp3_direct.output.samples_capacity = MAX_NCHAN * MAX_NGRAN * MAX_NSAMP;
    s_mp3_direct.output.samples_capacity_max = s_mp3_direct.output.samples_capacity * 2;
    s_mp3_direct.output.samples = heap_caps_malloc(s_mp3_direct.output.samples_capacity_max,
                                                 MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (!s_mp3_direct.output.samples) {
        s_mp3_direct.output.samples = malloc(s_mp3_direct.output.samples_capacity_max);
    }
    if (!s_mp3_direct.output.samples) {
        return ESP_ERR_NO_MEM;
    }
    s_mp3_direct.mp3_data.data_buf_size = MAINBUF_SIZE * 3;
    s_mp3_direct.mp3_data.data_buf = malloc(s_mp3_direct.mp3_data.data_buf_size);
    if (!s_mp3_direct.mp3_data.data_buf) {
        return ESP_ERR_NO_MEM;
    }
    s_mp3_direct.decoder = MP3InitDecoder();
    if (!s_mp3_direct.decoder) {
        return ESP_ERR_NO_MEM;
    }
    s_mp3_direct.ready = true;
    return ESP_OK;
}

static esp_err_t lexie_mono_to_stereo(decode_data *adata)
{
    size_t new_sample_count = adata->frame_count * 2;
    size_t bytes_needed = adata->frame_count * (adata->fmt.bits_per_sample / 8) * 2;
    if (bytes_needed > adata->samples_capacity_max) {
        return ESP_ERR_NO_MEM;
    }
    int16_t *samples = (int16_t *)adata->samples;
    int16_t *out = samples + (new_sample_count - 1);
    int16_t *in = samples + (adata->frame_count - 1);
    size_t frames = adata->frame_count;
    while (frames) {
        *out = *in;
        out--;
        *out = *in;
        out--;
        in--;
        frames--;
    }
    adata->fmt.channels = 2;
    return ESP_OK;
}

static esp_err_t lexie_mp3_direct_play(FILE *fp)
{
    esp_err_t ret = ESP_FAIL;
    format i2s_format = {0};

    if (lexie_mp3_direct_init() != ESP_OK) {
        ESP_LOGE(TAG, "MP3 direct init failed");
        fclose(fp);
        return ESP_FAIL;
    }

    lexie_mp3_reset_decoder();
    if (!s_mp3_direct.decoder) {
        ESP_LOGE(TAG, "MP3 decoder init failed");
        fclose(fp);
        return ESP_FAIL;
    }

    if (lexie_output_set_format(LEXIE_SAMPLE_RATE, 2, 16) != ESP_OK) {
        fclose(fp);
        return ESP_FAIL;
    }

    s_mp3_direct.mp3_data.bytes_in_data_buf = 0;
    s_mp3_direct.mp3_data.read_ptr = s_mp3_direct.mp3_data.data_buf;
    s_mp3_direct.mp3_data.eof_reached = false;

    while (true) {
        DECODE_STATUS decode_status =
            lexie_decode_mp3(s_mp3_direct.decoder, fp, &s_mp3_direct.output, &s_mp3_direct.mp3_data);

        if (decode_status == DECODE_STATUS_CONTINUE) {
            if (s_mp3_direct.output.fmt.channels == 1) {
                if (lexie_mono_to_stereo(&s_mp3_direct.output) != ESP_OK) {
                    ESP_LOGE(TAG, "mono->stereo failed");
                    break;
                }
            }
            uint32_t out_channels = s_mp3_direct.output.fmt.channels;
            if ((i2s_format.sample_rate != s_mp3_direct.output.fmt.sample_rate) ||
                (i2s_format.channels != out_channels) ||
                (i2s_format.bits_per_sample != s_mp3_direct.output.fmt.bits_per_sample)) {
                i2s_format = s_mp3_direct.output.fmt;
                if (lexie_output_set_format(i2s_format.sample_rate, out_channels,
                                            i2s_format.bits_per_sample) != ESP_OK) {
                    ESP_LOGE(TAG, "output format change failed sr=%u ch=%u",
                             (unsigned)i2s_format.sample_rate, (unsigned)out_channels);
                    break;
                }
            }
            size_t bytes_written = 0;
            size_t bytes_to_write = s_mp3_direct.output.frame_count * s_mp3_direct.output.fmt.channels *
                                    (i2s_format.bits_per_sample / 8);
            if (bsp_i2s_write(s_mp3_direct.output.samples, bytes_to_write, &bytes_written, portMAX_DELAY) !=
                ESP_OK) {
                break;
            }
            ret = ESP_OK;
        } else if (decode_status == DECODE_STATUS_NO_DATA_CONTINUE) {
            continue;
        } else if (decode_status == DECODE_STATUS_DONE) {
            ret = ESP_OK;
            break;
        } else {
            ESP_LOGE(TAG, "MP3 decode error status=%d", (int)decode_status);
            ret = ESP_FAIL;
            break;
        }
    }

    fclose(fp);
    vTaskDelay(pdMS_TO_TICKS(100));
    lexie_output_set_format(LEXIE_SAMPLE_RATE, 2, 16);
    return ret;
}

void lexie_set_pipeline_busy(bool busy)
{
    s_pipeline_busy = busy;
}

bool lexie_pipeline_is_busy(void)
{
    return s_pipeline_busy;
}

esp_err_t lexie_spiffs_init(void)
{
    esp_vfs_spiffs_conf_t conf = {
        .base_path = SPIFFS_MOUNT,
        .partition_label = "lexie_cfg",
        .max_files = 6,
        .format_if_mount_failed = false,
    };
    esp_err_t ret = esp_vfs_spiffs_register(&conf);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "SPIFFS mount failed: %s", esp_err_to_name(ret));
        return ret;
    }
    size_t total = 0, used = 0;
    esp_spiffs_info("lexie_cfg", &total, &used);
    ESP_LOGI(TAG, "SPIFFS lexie_cfg total=%u used=%u", (unsigned)total, (unsigned)used);
    return ESP_OK;
}

esp_err_t lexie_board_audio_init(void)
{
    I2C_Init();
    EXIO_Init();
    I2S_Init();
    ESP_ERROR_CHECK(lexie_mp3_direct_init());
    lexie_pa_enable(true);
    ESP_LOGI(TAG, "Codecs ready (ES8311 out + ES7210 in)");
    return ESP_OK;
}

static size_t build_wav(uint8_t *dst, const int16_t *samples, size_t sample_count)
{
    wav_header_t hdr = {
        .riff = {'R', 'I', 'F', 'F'},
        .wave = {'W', 'A', 'V', 'E'},
        .fmt = {'f', 'm', 't', ' '},
        .fmt_size = 16,
        .audio_format = 1,
        .num_channels = 1,
        .sample_rate = LEXIE_SAMPLE_RATE,
        .bits_per_sample = 16,
        .data = {'d', 'a', 't', 'a'},
    };
    hdr.byte_rate = LEXIE_SAMPLE_RATE * 2;
    hdr.block_align = 2;
    hdr.data_size = (uint32_t)(sample_count * sizeof(int16_t));
    hdr.chunk_size = 36 + hdr.data_size;

    memcpy(dst, &hdr, sizeof(hdr));
    memcpy(dst + sizeof(hdr), samples, sample_count * sizeof(int16_t));
    return sizeof(hdr) + sample_count * sizeof(int16_t);
}

esp_err_t lexie_record_ptt(int boot_gpio, uint8_t **wav_out, size_t *wav_len)
{
    if (!input_dev) {
        ESP_LOGE(TAG, "No input codec");
        return ESP_FAIL;
    }

    if (lexie_pipeline_is_busy()) {
        ESP_LOGW(TAG, "Pipeline busy — ignore PTT");
        return ESP_ERR_INVALID_STATE;
    }

    ESP_LOGI(TAG, "Hold BOOT to talk…");
    while (gpio_get_level(boot_gpio) != LEXIE_PTT_ACTIVE) {
        vTaskDelay(pdMS_TO_TICKS(50));
    }

    const size_t max_samples = LEXIE_SAMPLE_RATE * LEXIE_RECORD_MAX_SEC;
    int16_t *samples = heap_caps_malloc(max_samples * sizeof(int16_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (!samples) {
        samples = malloc(max_samples * sizeof(int16_t));
    }
    if (!samples) {
        return ESP_ERR_NO_MEM;
    }

    size_t sample_count = 0;
    int16_t chunk[512];
    TickType_t start = xTaskGetTickCount();

    while (gpio_get_level(boot_gpio) == LEXIE_PTT_ACTIVE && sample_count < max_samples) {
        esp_err_t err = esp_codec_dev_read(input_dev, chunk, sizeof(chunk));
        if (err != ESP_OK) {
            continue;
        }
        size_t got = sizeof(chunk) / sizeof(int16_t);
        memcpy(samples + sample_count, chunk, got * sizeof(int16_t));
        sample_count += got;
    }

    uint32_t elapsed_ms = (uint32_t)((xTaskGetTickCount() - start) * portTICK_PERIOD_MS);
    if (elapsed_ms < LEXIE_RECORD_MIN_MS) {
        ESP_LOGW(TAG, "Recording too short (%ums)", (unsigned)elapsed_ms);
        free(samples);
        return ESP_ERR_INVALID_SIZE;
    }

    size_t wav_size = sizeof(wav_header_t) + sample_count * sizeof(int16_t);
    uint8_t *wav = malloc(wav_size);
    if (!wav) {
        free(samples);
        return ESP_ERR_NO_MEM;
    }
    wav_size = build_wav(wav, samples, sample_count);
    free(samples);

    *wav_out = wav;
    *wav_len = wav_size;
    ESP_LOGI(TAG, "Recorded %u samples (~%ums)", (unsigned)sample_count, (unsigned)elapsed_ms);
    return ESP_OK;
}

static bool lexie_mp3_magic_ok(const uint8_t *data, size_t len)
{
    if (len < 4) {
        return false;
    }
    if (data[0] == 'I' && data[1] == 'D' && data[2] == '3') {
        return true;
    }
    if (data[0] == 0xFF && (data[1] & 0xE0) == 0xE0) {
        return true;
    }
    return false;
}

void lexie_audio_player_drain(void)
{
    vTaskDelay(pdMS_TO_TICKS(200));
    lexie_output_set_format(LEXIE_SAMPLE_RATE, 2, 16);
    lexie_mp3_reset_decoder();
}

static esp_err_t lexie_play_mp3_bytes_once(const uint8_t *data, size_t len)
{
    if (!lexie_mp3_magic_ok(data, len)) {
        ESP_LOGE(TAG, "MP3 header invalid (len=%u)", (unsigned)len);
        return ESP_FAIL;
    }

    lexie_audio_player_drain();

    FILE *play = fmemopen((void *)data, len, "rb");
    if (!play) {
        ESP_LOGE(TAG, "fmemopen failed len=%u", (unsigned)len);
        return ESP_FAIL;
    }

    return lexie_mp3_direct_play(play);
}

esp_err_t lexie_play_mp3_bytes(const uint8_t *data, size_t len)
{
    esp_err_t err = lexie_play_mp3_bytes_once(data, len);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Playback finished");
    }
    return err;
}

void lexie_play_error_beep(void)
{
    Play_Beep(220.0f);
}
