import boto3
import json
from datetime import datetime
import base64
import os  # 環境変数を読み込むためのモジュール

# 環境変数から設定を読み込む
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
SEQUENCE_TABLE = os.environ['SEQUENCE_TABLE']
MESSAGE_TABLE = os.environ['MESSAGE_TABLE']

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    # CORS対応のためのヘッダーを定義
    headers = {
        'Access-Control-Allow-Origin': '*',  # 必要に応じて特定のオリジンを指定
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }

    # OPTIONSメソッドの処理（プリフライトリクエストへの対応）
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    # POSTメソッドの処理
    if event['httpMethod'] == 'POST':
        # リクエストボディの取得
        body = json.loads(event['body'])
        name = body.get('name', '').strip()
        msg = body.get('msg', '').strip()

        # バリデーションチェック
        if not name or not msg:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'message': 'お名前と投稿内容は必須です'})
            }

        # 連番を更新ならびに取得
        seq_table = dynamodb.Table(SEQUENCE_TABLE)
        response = seq_table.update_item(
            Key={'tablename': 'message_board'},
            UpdateExpression='set seq = seq + :val',
            ExpressionAttributeValues={
                ':val': 1
            },
            ReturnValues='UPDATED_NEW'
        )
        nextval = int(response['Attributes']['seq'])

        has_image = 0
        # 画像の処理
        if 'image' in body:
            filename = f"{nextval}.jpg"
            data = base64.b64decode(body['image'])
            s3.put_object(Body=data, Bucket=S3_BUCKET_NAME, Key=filename, ContentType="image/jpeg")
            has_image = 1

        # メッセージデータの書き込み
        message_table = dynamodb.Table(MESSAGE_TABLE)
        message_table.put_item(
            Item={
                'id': nextval,
                'name': name,
                'msg': msg,
                'postat': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'has_image': has_image
            }
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'result': 1})
        }

    # その他のメソッドの場合
    return {
        'statusCode': 405,
        'headers': headers,
        'body': json.dumps({'message': 'Method Not Allowed'})
    }
