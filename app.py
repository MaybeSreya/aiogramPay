from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import CallbackQuery
import os
import asyncio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

API_TOKEN = '7764281853:AAHeUBgO5HzqNtzcjt3LxddaiVY0RGxQOFk'
CHANNEL_ID = '-1002379168520'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

keyboard = InlineKeyboardMarkup(row_width=2)
keyboard.add(
    InlineKeyboardButton("Received ✅", callback_data="received"),
    InlineKeyboardButton("Failed ❌", callback_data="failed")
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_payment_check', methods=['POST'])
def send_payment_check():
    asyncio.run(send_telegram_message())
    return jsonify({"message": "Moderator will check your payments!"})

async def send_telegram_message():
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text="Please verify the payment status:",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == "received")
async def process_received(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text("Payment received!", callback_query.message.chat.id, callback_query.message.message_id)
    socketio.emit('update_message', {"message": "Payment received!"})

@dp.callback_query_handler(lambda c: c.data == "failed")
async def process_failed(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text("Payment not received / payment failed!", callback_query.message.chat.id, callback_query.message.message_id)
    socketio.emit('update_message', {"message": "Payment not received / payment failed!"})

if __name__ == '__main__':
    from threading import Thread
    Thread(target=lambda: dp.start_polling(dp, skip_updates=True)).start()
    socketio.run(app, host="0.0.0.0", port=5000)
