#include "lexie_http.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "esp_crt_bundle.h"
#include "esp_heap_caps.h"
#include "esp_http_client.h"
#include "esp_log.h"

static const char *TAG = "lexie_http";

#define MAX_MP3_RESPONSE (512 * 1024)

typedef struct {
    uint8_t *buf;
    size_t len;
    size_t cap;
    int status;
} response_ctx_t;

static esp_err_t http_event_handler(esp_http_client_event_t *evt)
{
    response_ctx_t *ctx = (response_ctx_t *)evt->user_data;
    if (evt->event_id == HTTP_EVENT_ON_DATA && evt->data_len > 0 &&
        !esp_http_client_is_chunked_response(evt->client)) {
        if (ctx->len + evt->data_len > ctx->cap) {
            return ESP_FAIL;
        }
        memcpy(ctx->buf + ctx->len, evt->data, evt->data_len);
        ctx->len += evt->data_len;
    }
    return ESP_OK;
}

static void set_device_auth_headers(esp_http_client_handle_t client, const char *device_key)
{
    char auth[LEXIE_KEY_MAX + 16];
    snprintf(auth, sizeof(auth), "Bearer %s", device_key);
    esp_http_client_set_header(client, "Authorization", auth);
    esp_http_client_set_header(client, "X-Device-Key", device_key);
}

static esp_err_t http_get(const char *url, const char *device_key, response_ctx_t *ctx)
{
    esp_http_client_config_t config = {
        .url = url,
        .method = HTTP_METHOD_GET,
        .event_handler = http_event_handler,
        .user_data = ctx,
        .crt_bundle_attach = esp_crt_bundle_attach,
        .timeout_ms = 20000,
    };

    esp_http_client_handle_t client = esp_http_client_init(&config);
    if (!client) {
        return ESP_FAIL;
    }
    set_device_auth_headers(client, device_key);

    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) {
        ctx->status = esp_http_client_get_status_code(client);
    }
    esp_http_client_cleanup(client);
    return err;
}

static esp_err_t http_post_multipart(const char *url,
                                     const char *device_key,
                                     const uint8_t *wav,
                                     size_t wav_len,
                                     response_ctx_t *ctx)
{
    const char *boundary = "----LexieFormBoundary7MA4YWxk";
    char header_part[256];
    int header_part_len = snprintf(header_part, sizeof(header_part),
                                   "--%s\r\n"
                                   "Content-Disposition: form-data; name=\"audio\"; filename=\"audio.wav\"\r\n"
                                   "Content-Type: audio/wav\r\n\r\n",
                                   boundary);
    char footer[64];
    int footer_len = snprintf(footer, sizeof(footer), "\r\n--%s--\r\n", boundary);
    size_t body_len = (size_t)header_part_len + wav_len + (size_t)footer_len;

    uint8_t *body = malloc(body_len);
    if (!body) {
        return ESP_ERR_NO_MEM;
    }
    memcpy(body, header_part, (size_t)header_part_len);
    memcpy(body + header_part_len, wav, wav_len);
    memcpy(body + header_part_len + wav_len, footer, (size_t)footer_len);

    char content_type[80];
    snprintf(content_type, sizeof(content_type), "multipart/form-data; boundary=%s", boundary);

    esp_http_client_config_t config = {
        .url = url,
        .method = HTTP_METHOD_POST,
        /* open/write/read path — do not use http_event_handler or body is read twice */
        .crt_bundle_attach = esp_crt_bundle_attach,
        .timeout_ms = 90000,
    };

    esp_http_client_handle_t client = esp_http_client_init(&config);
    if (!client) {
        free(body);
        return ESP_FAIL;
    }

    set_device_auth_headers(client, device_key);
    esp_http_client_set_header(client, "Content-Type", content_type);
    esp_http_client_set_method(client, HTTP_METHOD_POST);

    esp_err_t err = esp_http_client_open(client, (int)body_len);
    if (err != ESP_OK) {
        esp_http_client_cleanup(client);
        free(body);
        return err;
    }
    if (esp_http_client_write(client, (const char *)body, body_len) < 0) {
        esp_http_client_cleanup(client);
        free(body);
        return ESP_FAIL;
    }
    free(body);

    int content_len = esp_http_client_fetch_headers(client);
    if (content_len < 0) {
        esp_http_client_cleanup(client);
        return ESP_FAIL;
    }
    ctx->status = esp_http_client_get_status_code(client);

    int read_total = 0;
    if (content_len > 0) {
        while (read_total < content_len && ctx->len < ctx->cap) {
            int to_read = (int)(ctx->cap - ctx->len);
            if (to_read > content_len - read_total) {
                to_read = content_len - read_total;
            }
            int r = esp_http_client_read(client, (char *)ctx->buf + ctx->len, to_read);
            if (r <= 0) {
                break;
            }
            ctx->len += (size_t)r;
            read_total += r;
        }
    } else {
        while (ctx->len < ctx->cap) {
            int r = esp_http_client_read(client, (char *)ctx->buf + ctx->len, (int)(ctx->cap - ctx->len));
            if (r <= 0) {
                break;
            }
            ctx->len += (size_t)r;
        }
    }
    if (content_len > 0 && (int)ctx->len != content_len) {
        ESP_LOGW(TAG, "body read %u bytes, expected %d", (unsigned)ctx->len, content_len);
        if ((int)ctx->len > content_len) {
            ctx->len = (size_t)content_len;
        }
        if ((int)ctx->len < content_len) {
            esp_http_client_close(client);
            esp_http_client_cleanup(client);
            return ESP_FAIL;
        }
    }

    const char *resp_ct = NULL;
    if (esp_http_client_get_header(client, "Content-Type", (char **)&resp_ct) == ESP_OK &&
        resp_ct && strstr(resp_ct, "audio/mpeg") == NULL &&
        strstr(resp_ct, "multipart") == NULL) {
        ESP_LOGW(TAG, "unexpected Content-Type: %s", resp_ct);
    }

    esp_http_client_close(client);
    esp_http_client_cleanup(client);
    return ESP_OK;
}

esp_err_t lexie_http_health(const lexie_config_t *cfg)
{
    char url[LEXIE_URL_MAX + 16];
    snprintf(url, sizeof(url), "%s/health", cfg->base_url);

    uint8_t *buf = malloc(256);
    if (!buf) {
        return ESP_ERR_NO_MEM;
    }
    response_ctx_t ctx = {.buf = buf, .cap = 256};

    esp_err_t err = http_get(url, cfg->device_key, &ctx);
    if (err != ESP_OK) {
        free(buf);
        ESP_LOGE(TAG, "health request failed: %s", esp_err_to_name(err));
        return err;
    }

    if (ctx.status != 200) {
        ESP_LOGE(TAG, "health HTTP %d", ctx.status);
        free(buf);
        return ESP_FAIL;
    }

    buf[ctx.len < 255 ? ctx.len : 255] = '\0';
    ESP_LOGI(TAG, "health OK: %s", (char *)buf);
    free(buf);
    return ESP_OK;
}

esp_err_t lexie_http_explain(const lexie_config_t *cfg,
                             const uint8_t *wav,
                             size_t wav_len,
                             lexie_http_body_t *out_mp3)
{
    char url[LEXIE_URL_MAX + 16];
    snprintf(url, sizeof(url), "%s/explain", cfg->base_url);

    ESP_LOGI(TAG, "POST /explain (device_key len=%u)", (unsigned)strlen(cfg->device_key));

    uint8_t *buf = heap_caps_malloc(MAX_MP3_RESPONSE, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (!buf) {
        buf = malloc(MAX_MP3_RESPONSE);
    }
    if (!buf) {
        return ESP_ERR_NO_MEM;
    }

    response_ctx_t ctx = {.buf = buf, .cap = MAX_MP3_RESPONSE};
    esp_err_t err = http_post_multipart(url, cfg->device_key, wav, wav_len, &ctx);
    if (err != ESP_OK) {
        free(buf);
        ESP_LOGE(TAG, "explain request failed: %s", esp_err_to_name(err));
        return err;
    }

    if (ctx.status != 200) {
        buf[ctx.len < 255 ? ctx.len : 255] = '\0';
        ESP_LOGE(TAG, "explain HTTP %d: %s", ctx.status, (char *)buf);
        free(buf);
        return ESP_FAIL;
    }

    if (ctx.len < 128) {
        ESP_LOGE(TAG, "explain body too small (%u bytes)", (unsigned)ctx.len);
        free(buf);
        return ESP_FAIL;
    }

    out_mp3->data = buf;
    out_mp3->len = ctx.len;
    ESP_LOGI(TAG, "explain OK, mp3 bytes=%u", (unsigned)ctx.len);
    return ESP_OK;
}

void lexie_http_body_free(lexie_http_body_t *body)
{
    if (body && body->data) {
        free(body->data);
        body->data = NULL;
        body->len = 0;
    }
}
