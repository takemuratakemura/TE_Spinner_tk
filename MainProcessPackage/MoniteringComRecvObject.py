from dataclasses import dataclass, asdict
@dataclass
class MoniteringComRecvObject:
    isStandbySW : int = 0
    isEmergencyStopSW : int = 0
    remoteControlAxisFB : float = 0
    remoteControlAxisLR : float = 0
    
    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)
