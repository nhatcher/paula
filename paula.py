import telepot
import toml
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import time
from picamera import PiCamera
from time import sleep
import glob
from PIL import Image
from tradfri import toggle

path = './images/'
fp_in = f"{path}image-*.png"
fp_out = 'time.gif'

camera = PiCamera()

config = toml.load('config.toml')

users = {}
for user in config['telegram']['users']:
    user[user['user_id']] = user['name']

bot = telepot.Bot(config['telegram']['token'])
index = 1

def on_chat_message(msg):
    print(f'Got message: {msg}')
    admin_id = config['telegram']['admin_id']
    # content_type, chat_type, chat_id = telepot.glance(msg)
    # print('Chat Message:', content_type, chat_type, chat_id)
    chat_id = msg['chat']['id']
    text = msg['text']
    command = text.lower()
    if not chat_id in users:
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Add user", callback_data=f'add_user: {chat_id}, '),
                InlineKeyboardButton(text="Reject", callback_data='reject')
            ]
        ])
        bot.sendMessage(admin_id, f"New contact {chat_id}: {text}", reply_markup=reply_markup)
    else:
        bot.sendMessage(chat_id, f"Hello {users[chat_id]}!")
        if chat_id != admin_id:
            bot.sendMessage(admin_id, "Got message from {}: {}".format(users[chat_id], text))
        if command.startswith('say'):
            bot.sendMessage(chat_id, text[4:])
        elif command.startswith("photo"):
            with open(f"{path}image-{index-1:03}.png", 'rb') as f:
                bot.sendPhoto(chat_id, f)
        elif command.startswith('timelapse'):
            # Makes a GIF of the last few pics.
            # We could get fancy here. We could do a timelapse between this and that every x seconds, for instance
            # With imageio we could do something like:
            # import imageio
            # import glob
            # images = []
            # for filename in sorted(glob.glob("*.png")):
            #     images.append(imageio.imread(filename))
            # imageio.mimsave('movie.mp4', images)

            last_ten = sorted(glob.glob(fp_in))[-10:]
            img = Image.open(last_ten.pop())
            imgs = [Image.open(f) for f in last_ten]
            img.save(fp=fp_out, format='GIF', append_images=imgs, save_all=True)#, duration=200, loop=0)
            with open(fp_out, 'rb') as f:
                bot.sendDocument(chat_id, f)
        elif command.startswith('lights'):
            toggle()

def on_callback_query(msg):
    admin_id = config['telegram']['admin_id']
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    if from_id == admin_id:
        if query_data.startswith('add_user:'):
            (user_id, user_name) = query_data[9:].split(',')
            users[user_id] = user_name
            bot.answerCallbackQuery(query_id, text='User added')
            bot.sendMessage(user_id, "Welcome! You are now an authorized user!")
        elif query_data.startswith('reject'):
            bot.answerCallbackQuery(query_id, text='User rejected')
    else:
        bot.answerCallbackQuery(query_id, text='Got it')


MessageLoop(bot, {
    'chat': on_chat_message,
    'callback_query': on_callback_query
}).run_as_thread()

print("Going into a loop")

while True:
    try:
        time.sleep(60)
        print("Take image {}".format(index))
        camera.capture(f"{path}image-{index:03}.png")
        index += 1
    except Exception as e:
        print("Exit")
        print(e)
        exit()