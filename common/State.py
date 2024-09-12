from enum import IntEnum

class State(IntEnum):
    IG_ON_MODE = 0
    PARKING_MODE  = 1
    DRIVE_MODE = 2
    FAIL_SAFE_MODE = 3
