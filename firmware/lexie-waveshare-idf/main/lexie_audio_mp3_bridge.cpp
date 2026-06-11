#include "lexie_audio_mp3_bridge.h"

#include "audio_mp3.h"

extern "C" bool lexie_is_mp3(FILE *fp)
{
    return is_mp3(fp);
}

extern "C" DECODE_STATUS lexie_decode_mp3(HMP3Decoder mp3_decoder, FILE *fp, decode_data *pData,
                                          mp3_instance *pInstance)
{
    return decode_mp3(mp3_decoder, fp, pData, pInstance);
}
