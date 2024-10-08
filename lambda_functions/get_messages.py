import json
import boto3
import decimal
import os  # 環境変数を読み込むためのモジュール

# 環境変数から設定を読み込む
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
MESSAGE_TABLE = os.environ['MESSAGE_TABLE']

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    message_table = dynamodb.Table(MESSAGE_TABLE)
    response = message_table.scan()

    # データをpostatの降順にソート
    sorted_items = sorted(response["Items"], reverse=True, key=lambda d: d["postat"])

    # 最大6件に制限
    limited_items = sorted_items[:6]

    # 各アイテムに画像URLを追加
    for item in limited_items:
        if item.get('has_image'):
            item['image_url'] = f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/{item["id"]}.jpg'
        else:
            item['image_url'] = None

    # Decimal型を変換するための関数
    def decimal_default(obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        raise TypeError

    # レスポンスデータの作成
    data = {
        'Items': limited_items
    }

    return {
        'statusCode': 200,
        'body': json.dumps(data, ensure_ascii=False, default=decimal_default),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # 必要に応じて特定のオリジンを指定
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        }
    }
