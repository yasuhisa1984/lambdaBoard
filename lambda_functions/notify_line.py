import os
import requests
import datetime
import boto3
import logging

# ログ設定
logger = logging.getLogger(__name__)
current_time = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')

# LINE Notifyの設定
TOKEN = os.environ["LINE_ACCESS_TOKEN"]
API_URL = 'https://notify-api.line.me/api/notify'

# 送信メッセージの設定
send_contents = f"新しい画像が投稿されました：{current_time}"
TOKEN_HEADERS = {'Authorization': 'Bearer ' + TOKEN}
send_data = {'message': send_contents}

# バイナリ形式で画像情報を取得
def get_image_from_s3(event):
    s3 = boto3.client('s3')
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    image_data = response['Body'].read()
    return image_data

def lambda_handler(event, context):
    try:
        # S3にアップロードされた画像を取得
        image_data = get_image_from_s3(event)
        image_file = {'imageFile': image_data}

        # LINE NotifyにPOSTリクエストを送信
        response = requests.post(API_URL, headers=TOKEN_HEADERS, data=send_data, files=image_file)
        response.raise_for_status()
        logger.info("LINE Notifyへの通知が成功しました")
        return {'statusCode': 200, 'body': 'Notification sent successfully'}
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        return {'statusCode': 500, 'body': 'Error sending notification'}
