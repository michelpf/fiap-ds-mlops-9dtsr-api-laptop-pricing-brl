from pathlib import Path
import src.app as app
import json

def test_model_exists():
    arquivo_path = Path("model/model.pkl")
    assert arquivo_path.is_file()

def test_model_version_exists():
    arquivo_path = Path("model/model_metadata.json")
    assert arquivo_path.is_file()

def test_handler_call():
    payload = {
        "brand": "dell",
        "processor_brand": "intel",
        "processor_name": "core i5",
        "os": "windows",
        "weight": "casual",
        "warranty": "2",
        "touchscreen": "0",
        "ram_gb": "16",
        "hdd": "0",
        "ssd": "256",
        "graphic_card": "8",
        "ram_type": "ddr4",
        "os_bit": "64"
    }

    event = {"data": payload}
    response = app.handler(event, None)
    
    response['body'] = json.loads(response['body'])

    assert isinstance(response["body"]["prediction"], int), "Prediction should be an integer"
    assert response["body"]["prediction"] > 0, "Prediction should be a non-negative integer"
    assert response["statusCode"] == 200, "Status code should be 200 OK"