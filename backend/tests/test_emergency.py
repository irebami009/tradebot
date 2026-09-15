from app.engine.emergency import EmergencyRiskController
from app.config import settings

def test_emergency_risk_controller():
    controller = EmergencyRiskController()
    
    assert not controller.is_active
    
    # Trigger emergency stop
    res = controller.trigger_emergency_stop("Test Emergency Trigger")
    assert res["emergency_stop"]
    assert controller.is_active
    assert settings.EMERGENCY_STOP

    # Reset emergency stop
    res_reset = controller.reset_emergency_stop()
    assert not res_reset["emergency_stop"]
    assert not settings.EMERGENCY_STOP
