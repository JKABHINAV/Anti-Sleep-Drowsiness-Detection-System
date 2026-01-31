#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/uart.h"
#include "esp_log.h"

// --- Configuration ---
#define BUZZER_PIN      18    // The GPIO pin connected to your Buzzer/LED
#define UART_PORT       UART_NUM_0
#define BUF_SIZE        1024
#define TAG             "ANTI_SLEEP_SYS"

/**
 * @brief Initialize UART for communication with the Laptop
 */
void init_uart() {
    const uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    // Install UART driver and configure parameters
    uart_driver_install(UART_PORT, BUF_SIZE * 2, 0, 0, NULL, 0);
    uart_param_config(UART_PORT, &uart_config);
    ESP_LOGI(TAG, "UART initialized at 115200 baud.");
}

/**
 * @brief Initialize GPIO for the Buzzer/Alarm
 */
void init_hw() {
    gpio_reset_pin(BUZZER_PIN);
    gpio_set_direction(BUZZER_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(BUZZER_PIN, 0); // Ensure buzzer is off at start
    ESP_LOGI(TAG, "GPIO Hardware initialized.");
}

void app_main(void) {
    // 1. Setup
    init_uart();
    init_hw();

    uint8_t *data = (uint8_t *) malloc(BUF_SIZE);

    ESP_LOGI(TAG, "System Started. Waiting for Python signals...");

    while (1) {
        // 2. Read data from Laptop (Serial)
        int len = uart_read_bytes(UART_PORT, data, BUF
