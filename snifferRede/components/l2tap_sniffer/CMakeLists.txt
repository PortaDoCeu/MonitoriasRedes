idf_component_register(
    SRCS "src/core/l2tap_sniffer_core.c"
         "src/backends/l2tap_sniffer_esp32_eth.c"
         "src/parser/l2tap_sniffer_parser.c"
    INCLUDE_DIRS "include"
    PRIV_INCLUDE_DIRS "src" "src/core" "src/backends" "src/parser"
    REQUIRES esp_driver_gpio esp_eth esp_event esp_netif esp_ringbuf esp_timer freertos lwip vfs
)