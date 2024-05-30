import os
import json
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import tempfile

# Environment variables for security
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Send me a Terabox link to download the video.")

def fetch_terabox_link(url: str) -> str:
    conn = http.client.HTTPSConnection("terabox-downloader-direct-download-link-generator.p.rapidapi.com")
    payload = json.dumps({"url": url})
    headers = {
        'content-type': "application/json",
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': "terabox-downloader-direct-download-link-generator.p.rapidapi.com"
    }
    conn.request("POST", "/fetch", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data)['directDownloadLink']  # Adjust based on API response structure

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if "terabox.app" in text:
        update.message.reply_text("Fetching the download link, please wait...")
        download_link = fetch_terabox_link(text)
        if download_link:
            update.message.reply_text("Downloading the video, please wait...")
            video_file = download_video(download_link)
            if video_file:
                with open(video_file, 'rb') as f:
                    update.message.reply_video(f)
                os.remove(video_file)
            else:
                update.message.reply_text("Failed to download the video.")
        else:
            update.message.reply_text("Failed to fetch the download link.")
    else:
        update.message.reply_text("Please send a valid Terabox link.")

def download_video(url: str) -> str:
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)
        tmp_file.close()
        return tmp_file.name
    return None

def main() -> None:
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
