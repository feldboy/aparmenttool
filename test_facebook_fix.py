#!/usr/bin/env python3
"""
Test script to debug and fix the Facebook setup finish issue
"""

def test_string_comparison():
    """Test various string comparison scenarios"""
    test_inputs = [
        "finish",
        "FINISH", 
        " finish ",
        "finish\n",
        "finish\r\n",
        "Finish",
        "'finish'",
        '"finish"',
        "done",
        "DONE"
    ]
    
    for input_str in test_inputs:
        cleaned = input_str.strip().lower()
        matches_finish = cleaned == 'finish'
        matches_done = cleaned == 'done'
        print(f"Input: '{input_str}' -> Cleaned: '{cleaned}' -> finish={matches_finish}, done={matches_done}")

if __name__ == "__main__":
    test_string_comparison()
