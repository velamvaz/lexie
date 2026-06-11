#pragma once

#include <stdbool.h>
#include <stdio.h>

#include "audio_decode_types.h"
#include "audio_mp3.h"
#include "mp3dec.h"

#ifdef __cplusplus
extern "C" {
#endif

bool lexie_is_mp3(FILE *fp);
DECODE_STATUS lexie_decode_mp3(HMP3Decoder mp3_decoder, FILE *fp, decode_data *pData, mp3_instance *pInstance);

#ifdef __cplusplus
}
#endif
