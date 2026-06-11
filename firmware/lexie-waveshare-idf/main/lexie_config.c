#include "lexie_config.h"

#include <ctype.h>
#include <stdio.h>
#include <string.h>

#include "cJSON.h"
#include "esp_log.h"

static const char *TAG = "lexie_cfg";

#define CONFIG_PATH "/spiffs/config.json"

static void trim_inplace(char *s)
{
    if (!s) {
        return;
    }
    size_t n = strlen(s);
    while (n > 0 && isspace((unsigned char)s[n - 1])) {
        s[--n] = '\0';
    }
    size_t start = 0;
    while (s[start] && isspace((unsigned char)s[start])) {
        start++;
    }
    if (start > 0) {
        memmove(s, s + start, strlen(s + start) + 1);
    }
}

esp_err_t lexie_config_load(lexie_config_t *out)
{
    if (!out) {
        return ESP_ERR_INVALID_ARG;
    }
    memset(out, 0, sizeof(*out));

    FILE *f = fopen(CONFIG_PATH, "r");
    if (!f) {
        ESP_LOGE(TAG, "Missing %s — run wx033-provision-idf.sh before flash", CONFIG_PATH);
        return ESP_FAIL;
    }

    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (len <= 0 || len > 8192) {
        fclose(f);
        return ESP_FAIL;
    }

    char *text = malloc((size_t)len + 1);
    if (!text) {
        fclose(f);
        return ESP_ERR_NO_MEM;
    }
    if (fread(text, 1, (size_t)len, f) != (size_t)len) {
        free(text);
        fclose(f);
        return ESP_FAIL;
    }
    text[len] = '\0';
    fclose(f);

    cJSON *root = cJSON_Parse(text);
    free(text);
    if (!root) {
        ESP_LOGE(TAG, "Invalid JSON in config");
        return ESP_FAIL;
    }

    cJSON *networks = cJSON_GetObjectItem(root, "networks");
    cJSON *base_url = cJSON_GetObjectItem(root, "base_url");
    cJSON *device_key = cJSON_GetObjectItem(root, "device_key");

    if (!cJSON_IsArray(networks) || !cJSON_IsString(base_url) || !cJSON_IsString(device_key)) {
        cJSON_Delete(root);
        return ESP_FAIL;
    }

    int count = cJSON_GetArraySize(networks);
    if (count < 1 || count > LEXIE_MAX_NETWORKS) {
        cJSON_Delete(root);
        return ESP_FAIL;
    }

    for (int i = 0; i < count; i++) {
        cJSON *item = cJSON_GetArrayItem(networks, i);
        cJSON *ssid = cJSON_GetObjectItem(item, "ssid");
        cJSON *password = cJSON_GetObjectItem(item, "password");
        if (!cJSON_IsString(ssid) || !cJSON_IsString(password)) {
            cJSON_Delete(root);
            return ESP_FAIL;
        }
        strncpy(out->networks[i].ssid, ssid->valuestring, LEXIE_SSID_MAX - 1);
        strncpy(out->networks[i].password, password->valuestring, LEXIE_PASS_MAX - 1);
        trim_inplace(out->networks[i].ssid);
        trim_inplace(out->networks[i].password);
    }
    out->network_count = (size_t)count;

    strncpy(out->base_url, base_url->valuestring, LEXIE_URL_MAX - 1);
    trim_inplace(out->base_url);
    if (out->base_url[strlen(out->base_url) - 1] == '/') {
        out->base_url[strlen(out->base_url) - 1] = '\0';
    }
    strncpy(out->device_key, device_key->valuestring, LEXIE_KEY_MAX - 1);
    trim_inplace(out->device_key);

    cJSON_Delete(root);
    ESP_LOGI(TAG, "Loaded config: %u network(s), base_url=%s, key_len=%u",
             (unsigned)out->network_count, out->base_url, (unsigned)strlen(out->device_key));
    return ESP_OK;
}
