#include <stdio.h>
#include <string.h>

/**
 * A simple C utility to validate the format of an AyurChain Product ID.
 * Returns 1 if valid (starts with PRD-), 0 otherwise.
 */
int validate_product_id(const char* id) {
    if (id == NULL) return 0;
    
    // Check if it starts with "PRD-"
    if (strncmp(id, "PRD-", 4) == 0) {
        return 1;
    }
    
    return 0;
}

// Main function for standalone testing
int main() {
    printf("Testing PRD-1234: %d\n", validate_product_id("PRD-1234"));
    printf("Testing XYZ-1234: %d\n", validate_product_id("XYZ-1234"));
    return 0;
}
