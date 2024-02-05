#include <stdio.h>
#include <stdint.h>

#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "vendor/stb_image.h"
#include "vendor/stb_image_write.h"

void makeBlackAndWhite(uint8_t* data, uint32_t width, uint32_t height, uint32_t inchannels, uint8_t* output){
    for(int y = 0; y < height; y++){
        for (int x = 0; x < width; x++){
            uint32_t p1 = (y * width + x);
            uint32_t p  = ((y * width) + x) * inchannels * 4;

            output[p1] = (data[p] * 0.3 + data[p+1] * 0.59 + data[p+2] * 0.11);
        }
    }
}

//ASSUMES BW
void denoise(uint8_t* data, uint32_t width, uint32_t height, uint8_t* output){
    for(int y = 0; y < height; y++){
        for (int x = 0; x < width; x++){
            uint16_t fcol = 0;

            int bsmat[5][5] = { 
                {  1,  4,  6,  4,  1 },
                {  4, 16, 24, 16,  4 },
                {  6, 24, 36, 24,  6 },
                {  4, 16, 24, 16,  4 },
                {  1,  4,  6,  4,  1 },
            };

            for(int i = 0; i < 5; i++){
                for (int j = 0; j < 5; j++){
                    int xi = x + (i - 2);
                    int yj = y + (j - 2);
                    
                    if (!(xi >= width || xi < 0 || yj >= height || yj < 0))
                        fcol += data[(yj * width) + xi] * bsmat[i][j];
                }
            }
            output[y * width + x] = fcol >> 8;
        }
    }
}

int main(){
    uint32_t x, y, n;
    uint8_t *data = stbi_load("caroline.jpg", &x, &y, &n, 0);
    uint8_t *data2 = malloc(x * y / 16);
    uint8_t *data3 = malloc(x * y / 16);

    makeBlackAndWhite(data, x/4, y/4, n, data2);
    stbi_write_bmp("carolinebw.bmp", x/4, y/4, 1, data2);
    printf("hello world\n");
    denoise(data2, x/4, y/4, data3);


    free(data2);
    stbi_image_free(data);
}