# This registers the 'main' component to the ESP-IDF build system
idf_component_register(
    SRCS "main.c"             # Add other .c files here if you create them
    INCLUDE_DIRS "."          # Tells the compiler to look for headers in this folder
)
