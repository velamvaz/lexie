#include "SD_MMC.h"

#include <stdio.h>

FILE *Open_File(const char *file_path)
{
    return fopen(file_path, "rb");
}
