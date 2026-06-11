#pragma once

#include <stdbool.h>
#include "driver/gpio.h"

#define BOOT_KEY_PIN            GPIO_NUM_0
#define Button_PIN1 BOOT_KEY_PIN
#define BUTTON_ACTIVE_LEVEL 0

extern bool BOOT_State;
extern bool KEY1_State;
extern bool KEY2_State;
extern bool KEY3_State;
