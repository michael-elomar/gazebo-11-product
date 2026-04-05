TARGET_OS := linux
TARGET_OS_FLAVOUR := native
TARGET_CC_PATH := /usr/bin/gcc
TARGET_LIBC := native
TARGET_GLOBAL_CFLAGS += -std=gnu99
USE_ADDRESS_SANITIZER := 0

prebuilt.json.override := 1
