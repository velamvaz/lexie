cmake_minimum_required(VERSION 3.16)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)

project(lexie-waveshare)

spiffs_create_partition_image(lexie_cfg ${CMAKE_CURRENT_SOURCE_DIR}/spiffs_image FLASH_IN_PROJECT)
