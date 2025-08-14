"""
Convert an int to VRChat Float8, capped from 0 to 100 both included
VRChat Float8 is [0,255] mapped uniformly to [-1,1]
Using only the range from 0.0 to 1.0 in this project
"""

def int2f8(value: int) -> float:
    """Convert integer [0...100] to VRChat Float8 [0.0 ... 1.0]"""
    value = max(0, min(100, value))
    return value / 100