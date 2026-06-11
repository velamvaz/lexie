#pragma once


#include <stdio.h>
#include "I2C_Driver.h"
#include "esp_io_expander_tca95xx_16bit.h"


/****************************************************** The macro defines the TCA9555PWR information ******************************************************/ 


#define I2C_ADDRESS         ESP_IO_EXPANDER_I2C_TCA9555_ADDRESS_000                   // TCA9555PWR I2C address

// esp_err_t i2c_master_init(void);                     // Example Initialize I2C to host mode
/********************************************************** Read EXIO status **********************************************************/       
bool Read_EXIO(uint32_t Pin);                           // Read the level of the TCA9555PWR Pin
/********************************************************** Set the EXIO output status **********************************************************/  
void Set_EXIO(uint32_t Pin,uint8_t State);              // Sets the level state of the Pin without affecting the other pins
/********************************************************* TCA9555PWR Initializes the device ***********************************************************/  
esp_err_t EXIO_Init(void);                              // Set the seven pins to PinState state, for example :PinState=0x23, 0010 0011 State (the highest bit is not used) (Output mode or input mode) 0= Output mode 1= Input mode. The default value is output mode


