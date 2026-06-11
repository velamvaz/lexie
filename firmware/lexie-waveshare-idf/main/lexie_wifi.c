#include "lexie_wifi.h"

#include <string.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "nvs_flash.h"

static const char *TAG = "lexie_wifi";

#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT BIT1

static EventGroupHandle_t s_wifi_events;
static bool s_wifi_started;

static int s_retry_count;
static const int s_max_retry = 8;

static void wifi_event_handler(void *arg, esp_event_base_t event_base, int32_t event_id, void *event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        wifi_event_sta_disconnected_t *disc = (wifi_event_sta_disconnected_t *)event_data;
        ESP_LOGW(TAG, "disconnect reason=%d", disc ? disc->reason : -1);
        if (s_retry_count < s_max_retry) {
            s_retry_count++;
            esp_wifi_connect();
        } else {
            xEventGroupSetBits(s_wifi_events, WIFI_FAIL_BIT);
        }
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        s_retry_count = 0;
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
    }
}

esp_err_t lexie_wifi_connect(const lexie_config_t *cfg)
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t wifi_cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&wifi_cfg));

    s_wifi_events = xEventGroupCreate();
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event_handler, NULL, NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event_handler, NULL, NULL));

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));

    for (size_t i = 0; i < cfg->network_count; i++) {
        xEventGroupClearBits(s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAIL_BIT);
        s_retry_count = 0;
        ESP_LOGI(TAG, "Trying SSID [%u]: %s", (unsigned)i, cfg->networks[i].ssid);

        wifi_config_t wcfg = {0};
        strncpy((char *)wcfg.sta.ssid, cfg->networks[i].ssid, sizeof(wcfg.sta.ssid) - 1);
        strncpy((char *)wcfg.sta.password, cfg->networks[i].password, sizeof(wcfg.sta.password) - 1);
        wcfg.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
        wcfg.sta.pmf_cfg.capable = true;
        wcfg.sta.pmf_cfg.required = false;

        ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wcfg));
        ESP_ERROR_CHECK(esp_wifi_start());
        ESP_ERROR_CHECK(esp_wifi_connect());

        EventBits_t bits = xEventGroupWaitBits(
            s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAIL_BIT, pdTRUE, pdFALSE, pdMS_TO_TICKS(45000));
        if (bits & WIFI_CONNECTED_BIT) {
            ESP_LOGI(TAG, "Connected to %s", cfg->networks[i].ssid);
            s_wifi_started = true;
            return ESP_OK;
        }
        ESP_LOGW(TAG, "Failed to join %s", cfg->networks[i].ssid);
        ESP_ERROR_CHECK(esp_wifi_stop());
    }

    return ESP_FAIL;
}

static bool lexie_wifi_link_up(void)
{
    wifi_ap_record_t ap;
    return esp_wifi_sta_get_ap_info(&ap) == ESP_OK;
}

esp_err_t lexie_wifi_ensure_connected(const lexie_config_t *cfg)
{
    (void)cfg;
    if (!s_wifi_events || !s_wifi_started) {
        return ESP_FAIL;
    }

    if (lexie_wifi_link_up()) {
        return ESP_OK;
    }

    ESP_LOGW(TAG, "Wi-Fi lost — reconnecting");
    s_retry_count = 0;
    xEventGroupClearBits(s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAIL_BIT);
    esp_wifi_connect();

    EventBits_t bits = xEventGroupWaitBits(
        s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAIL_BIT, pdFALSE, pdFALSE, pdMS_TO_TICKS(45000));
    if (bits & WIFI_CONNECTED_BIT) {
        ESP_LOGI(TAG, "Reconnected");
        return ESP_OK;
    }
    return ESP_FAIL;
}
