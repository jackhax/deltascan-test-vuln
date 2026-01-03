CC = gcc
CFLAGS = -fno-stack-protector -no-pie -g
TARGET = note_manager

all: $(TARGET)

$(TARGET): note_manager.c
	$(CC) $(CFLAGS) -o $(TARGET) note_manager.c

clean:
	rm -f $(TARGET)

# Build with ASAN for debugging (not for exploitation)
debug: note_manager.c
	$(CC) -fsanitize=address -g -o $(TARGET)_asan note_manager.c

.PHONY: all clean debug
