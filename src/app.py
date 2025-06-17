"""
Função para executar predição de valor de laptop com base nos parâmetros enviados, 
como modelo, processador, memória etc.
Utiliza modelo que precisa ser baixado do repositório de registro de modelos em toda 
implantação nova.
"""

from datetime import datetime
import json
import boto3
import joblib

model = joblib.load("model/model.pkl")

with open("model/model_metadata.json", "r", encoding="utf-8") as f:
    model_info = json.load(f)

cloudwatch = boto3.client("cloudwatch")

def write_real_data(data, prediction):
    """
    Função para escrever os dados consumidos para depois serem estudados 
    para desvios de dados, modelo ou conceito.

    Args:
        data (dict): dicionário de dados com todos os atributos.
        prediction (int): valor de predição
    """

    now = datetime.now()
    now_formatted = now.strftime("%d-%m-%Y %H:%M")

    file_name = f"{now.strftime('%Y-%m-%d')}_laptop_prediction_data.csv"

    data["price"] = prediction
    data["timestamp"] = now_formatted
    data["model_version"] = model_info["version"]

    s3 = boto3.client("s3")
    bucket_name = "fiap-ds-mlops"
    s3_path = "laptop-prediction-real-data-9dtsr"

    try:
        existing_object = s3.get_object(Bucket=bucket_name, Key=f'{s3_path}/{file_name}')
        existing_data = existing_object['Body'].read().decode('utf-8').strip().split('\n')
        existing_data.append(','.join(map(str, data.values())))
        updated_content = '\n'.join(existing_data)

    except s3.exceptions.NoSuchKey:
        updated_content = ','.join(data.keys()) + '\n' + ','.join(map(str, data.values()))


    s3.put_object(Body=updated_content, Bucket=bucket_name, Key=f'{s3_path}/{file_name}')


def input_metrics(data, prediction):
    """
    Função para escrever métricas customizadas no Cloudwatch.

    Args:
        data (dict): dicionário de dados com todos os atributos.
        prediction (int): valor de predição.
    """

    cloudwatch.put_metric_data(
        MetricData = [
            {
                'MetricName': 'Price Prediction',
                'Value': prediction,
                'Dimensions': [{'Name': "Currency", 'Value': "BRL"}]
            },
        ], Namespace='Laptop Pricing Model')

    for key, value in data.items():
        cloudwatch.put_metric_data(
        MetricData = [
            {
                'MetricName': 'Latptop Feature ',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [{'Name': key, 'Value': str(value)}]
            },
        ], Namespace='Laptop Pricing Features')

def prepare_payload(data):
    """
    Função para padronizar o payload de entrada de modo a 
    ser compatível com a execução do modelo.

    Args:
        data (dict): dicionário de dados com todos os atributos.

     Returns:
        dict: payload padronizado.
    """

    data_processed = []

    data_processed.append(int(data["ram_gb"]))
    data_processed.append(int(data["ssd"]))
    data_processed.append(int(data["hdd"]))
    data_processed.append(int(data["graphic_card"]))
    data_processed.append(int(data["warranty"]))

    conditions = {
        "brand": {"asus", "dell", "hp", "lenovo", "other"},
        "processor_brand": {"amd", "intel", "m1"},
        "processor_name": {"core i3", "core i5", "core i7", "other", "ryzen 5", "ryzen 7"},
        "os": {"other", "windows"},
        "weight": {"casual", "gaming", "thinnlight"},
        "touchscreen": {"0", "1"},
        "ram_type": {"ddr4", "other"},
        "os_bit": {"32", "64"}
    }

    for key, values in conditions.items():
        for value in values:
            data_processed.append(1 if data[key] == value else 0)

    return data_processed

def handler(event, context=False):
    """
    Função de entrada para execução do modelo.

    Args:
        event (dict): dicionário de dados com todos os atributos.
        context (object, optional): contexto de execução (opcional).

    Returns:
        json: predição do preço do laptop em BRL.
    """

    print(event)
    print(context)

    if "body" in event:
        print("Body found in event, invoke by API Gateway")

        body_str = event.get("body", "{}")
        body = json.loads(body_str)
        print(body)
        data = body.get("data", {})
    else:
        print("No body found in event, invoke by Lambda.")
        data = event.get("data", {})

    print(data)

    data_processed = prepare_payload(data)

    prediction = model.predict([data_processed])

    prediction = int(prediction[0])

    print(f"Prediction: {prediction}")

    input_metrics(data, prediction)
    write_real_data(data, prediction)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "prediction": prediction,
            "version": model_info["version"],
        })
    }
