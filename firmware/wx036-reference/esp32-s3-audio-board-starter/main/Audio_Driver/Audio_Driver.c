#include "Audio_Driver.h"
#include <math.h>
#include <stdlib.h>
/*
 * SPDX-FileCopyrightText: 2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

static const char *TAG = "AUDIO";
uint8_t Volume = 60;

void Audio_PA_EN(){
    Set_EXIO(IO_EXPANDER_PIN_NUM_8,true);
    vTaskDelay(pdMS_TO_TICKS(50));
}
void Audio_PA_DIS(){
    Set_EXIO(IO_EXPANDER_PIN_NUM_8,false);
    vTaskDelay(pdMS_TO_TICKS(50));
}

static esp_err_t bsp_i2s_write(void *audio_buffer, size_t len, size_t *bytes_written, uint32_t timeout_ms) {
    uint8_t *samples = (uint8_t *)audio_buffer;
    size_t sample_count = len / sizeof(uint8_t);
    // 使用 esp_codec_dev_write 写入音频数据
    // 假设 output_dev 是音频设备的句柄， sample_count 是每次写入的字节数
    esp_err_t ret = esp_codec_dev_write(output_dev, samples, sample_count);

    // 如果需要更新已写入的字节数
    if (bytes_written) {
        *bytes_written = sample_count;  // 假设每次写入 sample_count 字节
    }

    return ret;
}

static esp_err_t bsp_i2s_reconfig_clk(uint32_t rate, uint32_t bits_cfg, i2s_slot_mode_t ch) {                                   // I2S Init
    esp_err_t ret = ESP_OK;
    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(rate),
        .slot_cfg = I2S_STD_PHILIP_SLOT_DEFAULT_CONFIG((i2s_data_bit_width_t)bits_cfg, ch),
        .gpio_cfg ={
            .mclk = BSP_I2S_MCLK,
            .bclk = BSP_I2S_SCLK,
            .ws = BSP_I2S_LCLK,
            .dout = BSP_I2S_DOUT,
            .din = I2S_GPIO_UNUSED,
        },
    };
    ret |= i2s_channel_disable(i2s_keep[0]->tx_handle);
    ret |= i2s_channel_reconfig_std_clock(i2s_keep[0]->tx_handle, &std_cfg.clk_cfg);
    ret |= i2s_channel_reconfig_std_slot(i2s_keep[0]->tx_handle, &std_cfg.slot_cfg);
    ret |= i2s_channel_enable(i2s_keep[0]->tx_handle);
    return ret;
}

static esp_err_t audio_mute_function(AUDIO_PLAYER_MUTE_SETTING setting) {                                                       // audio mute function
    ESP_LOGI(TAG, "mute setting %d", setting);
    if(setting)
        Audio_PA_EN();
    else
        Audio_PA_DIS();
    return ESP_OK;
}


static audio_player_callback_event_t expected_event;
static QueueHandle_t event_queue;
static audio_player_callback_event_t event;

static void audio_player_callback(audio_player_cb_ctx_t *ctx) {
    if (ctx->audio_event == AUDIO_PLAYER_CALLBACK_EVENT_IDLE) {
        ESP_LOGI(TAG, "Playback finished");
    }
    if (ctx->audio_event == expected_event) {
        xQueueSend(event_queue, &(ctx->audio_event), 0);
    }
}

void Volume_Loop(void *parameter)
{
    // Wireless_Init();
    // uint8_t Volume_Old = Volume;
    while(1)
    {
        if(BOOT_State){
            // Play WAV file when BOOT button is pressed
            // File is stored in SPIFFS flash partition
            Play_WAV_File("/spiffs/sample.wav");
            BOOT_State = 0;
        }
        if(KEY1_State){
            // if(Volume > 95)
            //     Volume = 100;
            // else
            //     Volume = Volume + 5;
            ESP_LOGI(TAG, "turn up the volume:%d",Volume);
            Play_Beep(440.0f);  // Play beep at 440 Hz when volume button is pressed
            KEY1_State = 0;
        }
        else if(KEY2_State){
            Play_Beep(660.0f);  // Play beep at 660 Hz when KEY2 is pressed
            KEY2_State = 0;
        }
        else if(KEY3_State){
            // if(Volume < 5)
            //     Volume = 0;
            // else
            //     Volume = Volume - 5;
            ESP_LOGI(TAG, "turn down the volume:%d",Volume);
            Play_Beep(880.0f);  // Play beep at 880 Hz when volume button is pressed
            KEY3_State = 0;
        }
        // if(Volume_Old != Volume){
        //     Volume_adjustment(Volume);
        //     Volume_Old = Volume;
        // }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    vTaskDelete(NULL);
}

void Audio_Init(void)
{
    xTaskCreatePinnedToCore(
        Volume_Loop,
        "Other Driver task",
        4096,
        NULL,
        3,
        NULL,
        0);
    audio_player_config_t config = {
        .mute_fn = audio_mute_function,
        .write_fn = bsp_i2s_write,
        .clk_set_fn = bsp_i2s_reconfig_clk,
        .priority = 3,
        .coreID = 1
    };
    esp_err_t ret = audio_player_new(config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to create audio player: %s", esp_err_to_name(ret));
        return;
    }
    event_queue = xQueueCreate(1, sizeof(audio_player_callback_event_t));
    if (!event_queue) {
        ESP_LOGE(TAG, "Failed to create event queue");
        return;
    }
    ret = audio_player_callback_register(audio_player_callback, NULL);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to register callback: %s", esp_err_to_name(ret));
        return;
    }
    if (audio_player_get_state() != AUDIO_PLAYER_STATE_IDLE) {
        ESP_LOGE(TAG, "Expected state to be IDLE");                 // The player is not idle
        return;
    }
    Audio_PA_EN();

}
void Volume_adjustment(uint8_t Vol) {
    if(Vol > Volume_MAX )
        printf("Audio : The volume value is incorrect. Please enter 0 to 21\r\n");
    else
        Volume = Vol;
    esp_err_t ret = esp_codec_dev_set_out_vol(output_dev, Volume);
    if(ret != ESP_OK)
        ESP_LOGE("Audio", "esp_codec_dev_set_out_vol - The return value is not ESP_OK");
    ESP_LOGI(TAG, "Volume set to %d", Volume);
}

void Play_Beep(float frequency) {
    // Stop any currently playing audio first
    audio_player_state_t state = audio_player_get_state();
    if (state == AUDIO_PLAYER_STATE_PLAYING || state == AUDIO_PLAYER_STATE_PAUSE) {
        audio_player_stop();
        vTaskDelay(pdMS_TO_TICKS(50)); // Give it time to stop
    }

    const uint16_t sample_rate = 16000;
    const float duration_ms = 100.0f;  // 100ms duration
    const uint16_t num_samples = (uint16_t)(sample_rate * duration_ms / 1000.0f);
    const float amplitude = 0.3f;    // 30% volume for beep

    #ifndef M_PI
    #define M_PI 3.14159265358979323846
    #endif

    // Reconfigure I2S clock to beep sample rate (WAV file may have changed it)
    bsp_i2s_reconfig_clk(sample_rate, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO);
    vTaskDelay(pdMS_TO_TICKS(10)); // Allow clock to settle

    // Allocate buffer for stereo 16-bit samples
    int16_t *audio_buffer = (int16_t *)malloc(num_samples * 2 * sizeof(int16_t));
    if (audio_buffer == NULL) {
        ESP_LOGE(TAG, "Failed to allocate memory for beep");
        return;
    }

    // Generate sine wave for left and right channels
    for (uint16_t i = 0; i < num_samples; i++) {
        float sample = amplitude * sinf(2.0f * M_PI * frequency * i / sample_rate);
        int16_t sample_value = (int16_t)(sample * 32767.0f);
        audio_buffer[i * 2] = sample_value;     // Left channel
        audio_buffer[i * 2 + 1] = sample_value; // Right channel
    }

    // Enable audio PA before playing
    Audio_PA_EN();

    // Write to audio output
    esp_err_t ret = esp_codec_dev_write(output_dev, audio_buffer, num_samples * 2 * sizeof(int16_t));
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to write beep audio: %s", esp_err_to_name(ret));
        free(audio_buffer);
        return;
    }

    ESP_LOGI(TAG, "Beep played");

    // Wait for the beep to finish playing (100ms)
    vTaskDelay(pdMS_TO_TICKS(duration_ms));

    // Write a large silence buffer to flush the I2S DMA buffer and stop playback
    // I2S typically has DMA buffers of several hundred samples, so we write enough silence to clear it
    const uint16_t silence_samples = (uint16_t)(sample_rate * 200.0f / 1000.0f); // 200ms of silence
    int16_t *silence_buffer = (int16_t *)calloc(silence_samples * 2, sizeof(int16_t));
    if (silence_buffer != NULL) {
        esp_codec_dev_write(output_dev, silence_buffer, silence_samples * 2 * sizeof(int16_t));
        free(silence_buffer);
        // Wait for silence to be written
        vTaskDelay(pdMS_TO_TICKS(50));
    }

    // Disable and re-enable I2S channel to flush any remaining buffers
    if (i2s_keep[0] && i2s_keep[0]->tx_handle) {
        i2s_channel_disable(i2s_keep[0]->tx_handle);
        vTaskDelay(pdMS_TO_TICKS(10));
        i2s_channel_enable(i2s_keep[0]->tx_handle);
    }

    free(audio_buffer);
}

void Play_WAV_File(const char* filepath) {
    ESP_LOGI(TAG, "Attempting to play WAV file: %s", filepath);

    // Stop any currently playing audio first
    audio_player_state_t state = audio_player_get_state();
    if (state == AUDIO_PLAYER_STATE_PLAYING || state == AUDIO_PLAYER_STATE_PAUSE) {
        audio_player_stop();
        vTaskDelay(pdMS_TO_TICKS(100)); // Give it time to stop
    }

    // Open the WAV file
    FILE *wav_file = Open_File(filepath);
    if (wav_file == NULL) {
        ESP_LOGE(TAG, "Failed to open WAV file: %s - file may not exist", filepath);
        // Fallback to beep if file not found
        Play_Beep(800.0f);  // Default beep at 800 Hz
        return;
    }

    ESP_LOGI(TAG, "WAV file opened successfully, starting playback");

    // Use the existing audio player to play the WAV file
    // The audio player automatically detects WAV files and uses the appropriate decoder
    expected_event = AUDIO_PLAYER_CALLBACK_EVENT_PLAYING;
    esp_err_t ret = audio_player_play(wav_file);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to play WAV file: %s", esp_err_to_name(ret));
        fclose(wav_file);
        return;
    }

    // Wait for the playing event
    if (xQueueReceive(event_queue, &event, pdMS_TO_TICKS(500)) != pdPASS) {
        ESP_LOGE(TAG, "Failed to receive playing event - timeout");
        fclose(wav_file);
        return;
    }

    // Verify the player is actually playing
    state = audio_player_get_state();
    if (state != AUDIO_PLAYER_STATE_PLAYING) {
        ESP_LOGE(TAG, "Player state is not PLAYING (state: %d)", state);
        fclose(wav_file);
        return;
    }

    Audio_PA_EN();
    ESP_LOGI(TAG, "WAV file playback started successfully: %s", filepath);
}
