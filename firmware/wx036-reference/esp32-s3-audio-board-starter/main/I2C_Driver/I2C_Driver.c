#include "I2C_Driver.h"

static const char *I2C_TAG = "I2C";

i2c_master_bus_handle_t i2c_handle = NULL;
i2c_master_dev_handle_t i2c_driver = NULL;
static esp_err_t i2c_master_init(void)
{
    const i2c_master_bus_config_t bus_config = {
        .i2c_port = I2C_MASTER_NUM,
        .sda_io_num = I2C_SDA_IO,
        .scl_io_num = I2C_SCL_IO,
        .clk_source = I2C_CLK_SRC_DEFAULT,
    };

    esp_err_t ret = i2c_new_master_bus(&bus_config, &i2c_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(I2C_TAG, "Failed to initialize I2C bus: %s", esp_err_to_name(ret));
        return ret;
    }

    ESP_LOGI(I2C_TAG, "I2C bus initialized successfully");
    return ESP_OK;  // 返回 ESP_OK 表示成功
}


void I2C_Init(void)
{
    /********************* I2C *********************/
    ESP_ERROR_CHECK(i2c_master_init());
}


// Reg addr is 8 bit
// esp_err_t I2C_Write(uint8_t Driver_addr, uint8_t Reg_addr, const uint8_t *Reg_data, uint32_t Length)
// {
//     uint8_t buf[Length + 1];  // 为寄存器地址和数据分配空间
//     buf[0] = Reg_addr;        // 第一个字节为寄存器地址
//     memcpy(&buf[1], Reg_data, Length);  // 将数据复制到缓冲区

//     esp_err_t ret = i2c_master_write_to_device(i2c_handle, Driver_addr, buf, Length + 1, I2C_MASTER_TIMEOUT_MS / portTICK_PERIOD_MS);
//     if (ret != ESP_OK) {
//         ESP_LOGE(I2C_TAG, "I2C write failed: %s", esp_err_to_name(ret));
//     }
//     return ret;
// }
// esp_err_t I2C_Read(uint8_t Driver_addr, uint8_t Reg_addr, uint8_t *Reg_data, uint32_t Length)
// {
//     esp_err_t ret = i2c_master_write_read_device(i2c_handle, Driver_addr, &Reg_addr, 1, Reg_data, Length, I2C_MASTER_TIMEOUT_MS / portTICK_PERIOD_MS);
//     if (ret != ESP_OK) {
//         ESP_LOGE(I2C_TAG, "I2C read failed: %s", esp_err_to_name(ret));
//     }
//     return ret;
// }
