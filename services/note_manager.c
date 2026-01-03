/*
 * Note Manager - A simple note-taking application
 * Compile: make
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_NOTES 10
#define NOTE_SIZE 64

// Function pointer type for note operations
typedef void (*note_handler_t)(void);

// Note structure - contains data and a function pointer
typedef struct {
    char content[NOTE_SIZE];
    note_handler_t on_view;
} Note;

// Global note storage
Note *notes[MAX_NOTES] = {NULL};

// Flag to check if admin was called
int admin_accessed = 0;

// Regular view handler
void view_note_handler(void) {
    printf("[*] Note viewed successfully\n");
}

void admin_panel(void) {
    admin_accessed = 1;
    printf("\n[!] ADMIN PANEL ACCESSED\n");
    printf("[!] Exploitation successful!\n\n");
}

// Create a new note
int create_note(int index) {
    if (index < 0 || index >= MAX_NOTES) {
        printf("[-] Invalid index\n");
        return -1;
    }

    if (notes[index] != NULL) {
        printf("[-] Note already exists at index %d\n", index);
        return -1;
    }

    notes[index] = (Note *)malloc(sizeof(Note));
    if (notes[index] == NULL) {
        printf("[-] Failed to allocate memory\n");
        return -1;
    }

    memset(notes[index]->content, 0, NOTE_SIZE);
    notes[index]->on_view = view_note_handler;

    printf("[+] Note created at index %d\n", index);
    printf("[DEBUG] Note address: %p\n", (void *)notes[index]);
    printf("[DEBUG] Handler address: %p\n", (void *)notes[index]->on_view);
    return 0;
}

// Edit note content
int edit_note(int index, const char *content) {
    if (index < 0 || index >= MAX_NOTES) {
        printf("[-] Invalid index\n");
        return -1;
    }

    if (notes[index] == NULL) {
        printf("[-] No note at index %d\n", index);
        return -1;
    }

    strncpy(notes[index]->content, content, NOTE_SIZE - 1);
    notes[index]->content[NOTE_SIZE - 1] = '\0';

    printf("[+] Note edited at index %d\n", index);
    return 0;
}

// View a note - calls the handler function pointer
int view_note(int index) {
    if (index < 0 || index >= MAX_NOTES) {
        printf("[-] Invalid index\n");
        return -1;
    }

    if (notes[index] == NULL) {
        printf("[-] No note at index %d\n", index);
        return -1;
    }

    printf("[*] Note %d: %s\n", index, notes[index]->content);

    if (notes[index]->on_view != NULL) {
        notes[index]->on_view();
    }

    return 0;
}

int delete_note(int index) {
    if (index < 0 || index >= MAX_NOTES) {
        printf("[-] Invalid index\n");
        return -1;
    }

    if (notes[index] == NULL) {
        printf("[-] No note at index %d\n", index);
        return -1;
    }

    free(notes[index]);
    printf("[+] Note deleted at index %d\n", index);
    return 0;
}

// Allocate a custom buffer
void *alloc_buffer(size_t size) {
    void *buf = malloc(size);
    printf("[DEBUG] Allocated buffer at %p (size: %zu)\n", buf, size);
    return buf;
}

// Write to a buffer
void write_buffer(void *buf, const char *data, size_t len) {
    if (buf == NULL) {
        printf("[-] Invalid buffer\n");
        return;
    }
    memcpy(buf, data, len);
    printf("[+] Written %zu bytes to buffer\n", len);
}

void print_menu(void) {
    printf("\n=== Note Manager v1.0 ===\n");
    printf("1. Create note\n");
    printf("2. Edit note\n");
    printf("3. View note\n");
    printf("4. Delete note\n");
    printf("5. Allocate buffer\n");
    printf("6. Write to buffer\n");
    printf("7. Show addresses (debug)\n");
    printf("8. Exit\n");
    printf("Choice: ");
}

void show_debug_info(void) {
    printf("\n[DEBUG] Address information:\n");
    printf("  admin_panel() @ %p\n", (void *)admin_panel);
    printf("  view_note_handler() @ %p\n", (void *)view_note_handler);
    printf("  Note size: %zu bytes\n", sizeof(Note));
    printf("  Content offset: 0\n");
    printf("  Handler offset: %zu\n", offsetof(Note, on_view));

    for (int i = 0; i < MAX_NOTES; i++) {
        if (notes[i] != NULL) {
            printf("  notes[%d] @ %p (handler: %p)\n", i,
                   (void *)notes[i], (void *)notes[i]->on_view);
        }
    }
}

int main(void) {
    int choice, index;
    char content[256];
    void *current_buffer = NULL;
    size_t buf_size;

    // Disable buffering for cleaner output
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    printf("=== Note Manager v1.0 ===\n");

    while (1) {
        print_menu();

        if (scanf("%d", &choice) != 1) {
            printf("[-] Invalid input\n");
            while (getchar() != '\n');
            continue;
        }
        getchar(); // consume newline

        switch (choice) {
            case 1: // Create
                printf("Index (0-%d): ", MAX_NOTES - 1);
                scanf("%d", &index);
                getchar();
                create_note(index);
                break;

            case 2: // Edit
                printf("Index (0-%d): ", MAX_NOTES - 1);
                scanf("%d", &index);
                getchar();
                printf("Content: ");
                fgets(content, sizeof(content), stdin);
                content[strcspn(content, "\n")] = 0;
                edit_note(index, content);
                break;

            case 3: // View
                printf("Index (0-%d): ", MAX_NOTES - 1);
                scanf("%d", &index);
                getchar();
                view_note(index);
                break;

            case 4: // Delete
                printf("Index (0-%d): ", MAX_NOTES - 1);
                scanf("%d", &index);
                getchar();
                delete_note(index);
                break;

            case 5: // Alloc buffer
                printf("Size: ");
                scanf("%zu", &buf_size);
                getchar();
                current_buffer = alloc_buffer(buf_size);
                break;

            case 6: // Write buffer
                if (current_buffer == NULL) {
                    printf("[-] No buffer allocated\n");
                    break;
                }
                printf("Data (hex, e.g., 41414141): ");
                fgets(content, sizeof(content), stdin);
                content[strcspn(content, "\n")] = 0;

                // Parse hex input
                size_t len = strlen(content) / 2;
                unsigned char *data = malloc(len);
                for (size_t i = 0; i < len; i++) {
                    sscanf(content + i*2, "%2hhx", &data[i]);
                }
                write_buffer(current_buffer, (char *)data, len);
                free(data);
                break;

            case 7: // Debug
                show_debug_info();
                break;

            case 8: // Exit
                printf("[*] Goodbye!\n");
                return 0;

            default:
                printf("[-] Invalid choice\n");
        }

        // Check if admin was accessed
        if (admin_accessed) {
            printf("\n[*] Challenge completed! Exiting...\n");
            return 0;
        }
    }

    return 0;
}
