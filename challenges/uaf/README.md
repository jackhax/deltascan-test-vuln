# Use-After-Free Challenge

## Objective
Exploit the Use-After-Free vulnerability to call `admin_panel()` and capture the flag.

## Build
```bash
make
```

## Run
```bash
./note_manager
```

## Vulnerability
The `delete_note()` function frees the note's memory but **does not set the pointer to NULL**. This creates a dangling pointer that can be exploited.

## Exploitation Strategy

1. **Create a note** - This allocates a `Note` struct containing content and a function pointer
2. **Delete the note** - Memory is freed but pointer still exists (dangling pointer)
3. **Allocate a new buffer of the same size** - Heap allocator may return the same memory
4. **Overwrite the function pointer** - Write the address of `admin_panel()` where `on_view` was
5. **View the deleted note** - Triggers the UAF, calling your overwritten function pointer

## GDB Commands

```bash
# Start with GDB
gdb ./note_manager

# Set breakpoints
b view_note
b delete_note
b admin_panel

# Run
r

# After creating and deleting a note, examine memory
x/20gx <note_address>

# Check function addresses
p admin_panel
p view_note_handler

# Step through
ni / si
```

## Solution Hint

The Note struct is 72 bytes (64 content + 8 function pointer).
After freeing, allocate exactly 72 bytes and write `admin_panel`'s address
at offset 64 (where `on_view` was).

## Expected Flag
`CTF{us3_4ft3r_fr33_pwn3d}`
