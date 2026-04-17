import telebot
import json
import os

BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)

DATA_FILE = "videos.json"
user_waiting = {}

# Load saved videos
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        saved_videos = json.load(f)
else:
    saved_videos = {}


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(saved_videos, f, indent=4)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Welcome!\n\n"
        "Send me a video and I will ask you for a name.\n\n"
        "Commands:\n"
        "/call videoname - Get a saved video\n"
        "/calllist - Show all saved videos\n"
        "/delete videoname - Delete a video\n"
        "/rename oldname newname - Rename a video"
    )


@bot.message_handler(content_types=['video'])
def receive_video(message):
    user_id = str(message.from_user.id)
    file_id = message.video.file_id

    user_waiting[user_id] = {
        "file_id": file_id
    }

    bot.reply_to(message, "What name do you want to save this video as?")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()

    # Save video name after upload
    if user_id in user_waiting:
        video_name = text.lower()

        if user_id not in saved_videos:
            saved_videos[user_id] = {}

        saved_videos[user_id][video_name] = user_waiting[user_id]["file_id"]
        save_data()

        del user_waiting[user_id]

        bot.reply_to(message, f"Video saved as '{video_name}'")
        return

    # Retrieve video
    if text.startswith('/call '):
        video_name = text.replace('/call ', '').strip().lower()

        if user_id in saved_videos and video_name in saved_videos[user_id]:
            file_id = saved_videos[user_id][video_name]
            bot.send_video(message.chat.id, file_id, caption=f"Saved video: {video_name}")
        else:
            bot.reply_to(message, "No video found with that name.")
        return

    # List videos
    if text == '/calllist':
        if user_id in saved_videos and saved_videos[user_id]:
            names = "\n".join(saved_videos[user_id].keys())
            bot.reply_to(message, f"Your saved videos:\n\n{names}")
        else:
            bot.reply_to(message, "You have no saved videos.")
        return

    # Delete video
    if text.startswith('/delete '):
        video_name = text.replace('/delete ', '').strip().lower()

        if user_id in saved_videos and video_name in saved_videos[user_id]:
            del saved_videos[user_id][video_name]
            save_data()
            bot.reply_to(message, f"Deleted '{video_name}'")
        else:
            bot.reply_to(message, "No video found with that name.")
        return

    # Rename video
    if text.startswith('/rename '):
        parts = text.split()

        if len(parts) < 3:
            bot.reply_to(message, "Usage: /rename oldname newname")
            return

        old_name = parts[1].lower()
        new_name = parts[2].lower()

        if user_id in saved_videos and old_name in saved_videos[user_id]:
            saved_videos[user_id][new_name] = saved_videos[user_id][old_name]
            del saved_videos[user_id][old_name]
            save_data()
            bot.reply_to(message, f"Renamed '{old_name}' to '{new_name}'")
        else:
            bot.reply_to(message, "No video found with that old name.")
        return

    bot.reply_to(message, "Send a video or use commands.")


print("Bot is running...")
bot.infinity_polling()
