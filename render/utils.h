#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <math.h>
#include <pthread.h>
#include <assert.h>

#define BLOCK_SIZE 32
static pthread_mutex_t mutex;

bool REPETITION = true;
int repetition_time = 0; 
// 0: no shift;
// 1: shift to right by half of block;
// 2: shift to down by half of block

struct bit_ele {
    char bit;
    // struct bit_ele *former;
    struct bit_ele *next;
    void* first_bit;
    bool last_bit;
};

struct bit_map {
    struct bit_ele* ele_arr[BLOCK_SIZE][BLOCK_SIZE];
    // int curr_index;
};


struct bit_ele* read_swap_data(char* file_path) { // output: the first bit
    FILE *f;
    char char_buff;
    f = fopen(file_path, "r");
    if (f == NULL) {
        return NULL;
    }
    struct bit_ele* curr_bit;

    char_buff = fgetc(f);
    if (char_buff != EOF) {
        curr_bit = (struct bit_ele*) malloc(sizeof(struct bit_ele));
        curr_bit->bit = char_buff;
        curr_bit->first_bit = curr_bit;
        // curr_bit->former = NULL;
    } else return NULL;
    char_buff = fgetc(f);
    while(char_buff != EOF && char_buff != '\n') {
        struct bit_ele* next_bit = (struct bit_ele*) malloc(sizeof(struct bit_ele));
        curr_bit->next = next_bit;
        curr_bit->last_bit = false;
        // next_bit->former = curr_bit;
        next_bit->first_bit = curr_bit->first_bit;
        next_bit->bit = char_buff;
        curr_bit = curr_bit->next;
        char_buff = fgetc(f);
    }
    curr_bit->next = NULL;
    curr_bit->last_bit = true;
    return (struct bit_ele*) curr_bit->first_bit;
}


void free_bit_arr(struct bit_ele* barr) { // input: the first bit
    assert(barr == barr->first_bit);
    if (barr->last_bit) {
        free(barr);
        return;
    }
    struct bit_ele* temp;
    while(!barr->next->last_bit) {
        temp = barr;
        barr = barr->next;
        free(temp);
    }
    free(barr->next);
}

///////////////////////////////////////////////////////////
// Below functions are used for multiple values per frame.
///////////////////////////////////////////////////////////

struct bit_map* read_location_data(char* file_path) {
    FILE *f;
    char char_buff;
    f = fopen(file_path, "r");
    if (f == NULL) {
        return NULL;
    }
    struct bit_map* big_map;
    big_map = (struct bit_map*) malloc(sizeof(struct bit_map));
    // big_map->curr_index = 0;
    struct bit_ele* curr_bit;
    int line_num = 0;
    char_buff = fgetc(f);
    if (char_buff != EOF) {
        curr_bit = (struct bit_ele*) malloc(sizeof(struct bit_ele));
        curr_bit->bit = char_buff;
        curr_bit->first_bit = curr_bit;
        big_map->ele_arr[(int)floor(line_num / BLOCK_SIZE)][(int)(line_num - BLOCK_SIZE * floor(line_num / BLOCK_SIZE))] \
            = curr_bit;
        line_num ++;
        // curr_bit->former = NULL;
    } else return NULL;
    char_buff = fgetc(f);
    while(char_buff != EOF) {
        struct bit_ele* next_bit = (struct bit_ele*) malloc(sizeof(struct bit_ele));
        curr_bit->next = next_bit;
        curr_bit->last_bit = false;
        // next_bit->former = curr_bit;
        next_bit->first_bit = curr_bit->first_bit;
        next_bit->bit = char_buff;
        curr_bit = curr_bit->next;
        char_buff = fgetc(f);
        if (char_buff == '\n') {
            char_buff = fgetc(f);
            if (char_buff == EOF) break;
            curr_bit->next = NULL;
            curr_bit->last_bit = true;
            ////////////
            curr_bit = (struct bit_ele*) malloc(sizeof(struct bit_ele));
            curr_bit->bit = char_buff;
            curr_bit->first_bit = curr_bit;
            big_map->ele_arr[(int)floor(line_num / BLOCK_SIZE)][(int)(line_num - BLOCK_SIZE * floor(line_num / BLOCK_SIZE))] = curr_bit;
            char_buff = fgetc(f);
            line_num ++;
        }
    }
    curr_bit->next = NULL;
    curr_bit->last_bit = true;
    return big_map;

}

void free_location_data(struct bit_map* big_map) {
    for(int i = 0; i < BLOCK_SIZE; i++) {
        for(int j = 0; j < BLOCK_SIZE; j++) {
            free_bit_arr((struct bit_ele*) big_map->ele_arr[i][j]->first_bit);
        }
    }
    free(big_map);
}

int normalized_block_index(int raw) {
    if (raw < 0) return 0;

    if (raw >= BLOCK_SIZE) return BLOCK_SIZE - 1;

    return raw;
}

/***************************************
@x, @y: indexes of pixel
@bit_eles: location encoding data
@width, @height: size of monitor
****************************************/
char get_bit_by_pixel(int x, int y, struct bit_map* big_map, \
    int width, int height) {
        int bound = width > height ? height:width; // assume always height
        if((x > (width - bound)/2 + bound) || (x < (width - bound)/2)) return '1';

        int x_new, y_new;
        int pixels_per_block = bound / BLOCK_SIZE;
        ///////////////////shift
        if(repetition_time == 0) {
            x_new = x;
            y_new = y;
        }
        else if(repetition_time == 1) {
            x_new = x + (int) pixels_per_block / 2;
            y_new = y;
        }
        else {
            x_new = x;
            y_new = y + (int) pixels_per_block / 2;
        }
        ///////////////////shift

        int block_x = floor((x_new - ((width - bound)/2)) / pixels_per_block);
        int block_y = floor(y_new / pixels_per_block);
        block_x = normalized_block_index(block_x);
        block_y = normalized_block_index(block_y);
        return big_map->ele_arr[block_x][block_y]->bit;
}


void move_next(struct bit_map* big_map) {
    bool go_first = false;
    for(int i = 0; i < BLOCK_SIZE; i++) {
        for(int j = 0; j < BLOCK_SIZE; j++) {
            if(!big_map->ele_arr[i][j]->last_bit) {
                big_map->ele_arr[i][j] = big_map->ele_arr[i][j]->next;
            }
            else {
                big_map->ele_arr[i][j] = (struct bit_ele*) big_map->ele_arr[i][j]->first_bit;
                if(!go_first) go_first = true;
            }
        }
    }
    if(go_first) {
        pthread_mutex_lock(&mutex);
        if(repetition_time == 0) repetition_time = 1;
        else if(repetition_time == 1) repetition_time = 2;
        else {
            repetition_time = 0;
        }
        pthread_mutex_unlock(&mutex);
    }
}

