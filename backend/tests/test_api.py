from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["mode"] == "PAPER"

def test_get_status():
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert "is_running" in data
    assert "PAPER TRADING" in data["warning"]

def test_get_balance():
    res = client.get("/api/balance")
    assert res.status_code == 200
    data = res.json()
    assert "virtual_balance" in data
    assert "equity" in data

def test_get_trades():
    res = client.get("/api/trades")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_get_market():
    res = client.get("/api/market/BTC-USD?limit=10")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_emergency_endpoints():
    res = client.post("/api/emergency/trigger")
    assert res.status_code == 200
    assert res.json()["emergency_stop"]

    res_reset = client.post("/api/emergency/reset")
    assert res_reset.status_code == 200
    assert not res_reset.json()["emergency_stop"]

def test_backtest_endpoint():
    payload = {
        "symbol": "BTC/USD",
        "starting_balance": 10000.0,
        "risk_per_trade": 0.01,
        "stop_loss_percent": 0.02,
        "take_profit_percent": 0.04,
        "min_confidence": 75.0
    }
    res = client.post("/api/backtest", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["starting_balance"] == 10000.0
    assert "total_return_percent" in data
