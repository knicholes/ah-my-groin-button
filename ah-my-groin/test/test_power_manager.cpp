/*
 * Test file for PowerManager functionality
 * 
 * This file contains basic tests to verify PowerManager implementation
 * meets the requirements for deep sleep and power management.
 */

#include <Arduino.h>
#include <unity.h>
#include "PowerManager.h"

// Test PowerManager initialization
void test_power_manager_initialization() {
    PowerManager testManager(5, 2);
    
    // Test that manager initializes without crashing
    testManager.begin();
    
    // Test initial state
    TEST_ASSERT_TRUE(testManager.isAwake());
    TEST_ASSERT_FALSE(testManager.isDFPlayerEnabled());
}

// Test DFPlayer power control
void test_dfplayer_power_control() {
    PowerManager testManager(5, 2);
    testManager.begin();
    
    // Test enabling DFPlayer
    testManager.enableDFPlayer();
    TEST_ASSERT_TRUE(testManager.isDFPlayerEnabled());
    
    // Test disabling DFPlayer
    testManager.disableDFPlayer();
    TEST_ASSERT_FALSE(testManager.isDFPlayerEnabled());
}

// Test wake/sleep state management
void test_wake_sleep_states() {
    PowerManager testManager(5, 2);
    testManager.begin();
    
    // Test initial awake state
    TEST_ASSERT_TRUE(testManager.isAwake());
    
    // Test wake from sleep
    testManager.wakeFromSleep();
    TEST_ASSERT_TRUE(testManager.isAwake());
    
    // Test that last wake time is recorded
    unsigned long wakeTime = testManager.getLastWakeTime();
    TEST_ASSERT_TRUE(wakeTime > 0);
}

// Test peripheral power management
void test_peripheral_management() {
    PowerManager testManager(5, 2);
    testManager.begin();
    
    // Test disabling unused peripherals (should not crash)
    testManager.disableUnusedPeripherals();
    
    // Test re-enabling all peripherals (should not crash)
    testManager.enableAllPeripherals();
}

void setup() {
    // Initialize Unity test framework
    UNITY_BEGIN();
    
    // Run tests
    RUN_TEST(test_power_manager_initialization);
    RUN_TEST(test_dfplayer_power_control);
    RUN_TEST(test_wake_sleep_states);
    RUN_TEST(test_peripheral_management);
    
    // Finish testing
    UNITY_END();
}

void loop() {
    // Empty loop for testing
}