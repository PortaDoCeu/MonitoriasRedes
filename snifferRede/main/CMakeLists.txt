idf_component_register(
    SRCS "src/app/l2tap_sniffer_main.c"
         "src/output/sniffer_output.c"
    INCLUDE_DIRS "include"
    REQUIRES esp_event esp_netif l2tap_sniffer nvs_flash vfs
)
