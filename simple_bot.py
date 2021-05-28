import telepot
import toml

from telepot.loop import MessageLoop

# This is simple server bot that returns the chat_id to whoever sends a message
# You can use it to get your own user_id or to build more complex bots

# you can simply paste your token here (remember that it is secret)
token = toml.load('config.toml')['telegram']['token']

def on_chat_message(message):
    print(f'Got message: {message}')
    (content_type, chat_type, chat_id) = telepot.glance(message)
    bot.sendMessage(chat_id, f"Hello {chat_id}!")

print("Going into a loop")

bot = telepot.Bot(token)
MessageLoop(bot, on_chat_message).run_as_thread()

while True:
    pass