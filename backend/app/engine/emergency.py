from typing import Dict, Any, List
from app.config import settings

class EmergencyRiskController:
    """
    Emergency Risk Controller and Kill Switch manager.
    Protects real capital during extreme volatility, API outages, or unexpected drawdown events.
    """
    def __init__(self):
        self._emergency_stop = settings.EMERGENCY_STOP

    @property
    def is_active(self) -> bool:
        return self._emergency_stop or settings.EMERGENCY_STOP

    def trigger_emergency_stop(self, reason: str = "Manual Emergency Kill Switch Activated") -> Dict[str, Any]:
        """
        Activates global emergency stop switch.
        """
        self._emergency_stop = True
        settings.EMERGENCY_STOP = True
        print(f"[EMERGENCY RISK CONTROLLER] GLOBAL KILL SWITCH ACTIVATED: {reason}")
        return {
            "emergency_stop": True,
            "status": "ACTIVATED",
            "reason": reason
        }

    def reset_emergency_stop(self) -> Dict[str, Any]:
        """
        Resets emergency stop after human review.
        """
        self._emergency_stop = False
        settings.EMERGENCY_STOP = False
        print("[EMERGENCY RISK CONTROLLER] Emergency stop reset by user.")
        return {
            "emergency_stop": False,
            "status": "RESET"
        }
