from pyrogram import Client,filters
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup

@Client.on_message(filters.command("settings") & filters.private)
async def settings_panel(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    keyboard=InlineKeyboardMarkup([
        [InlineKeyboardButton("Force Subscription",callback_data="admin:fsub")],
        [InlineKeyboardButton("Storage Channels",callback_data="admin:storage")],
        [InlineKeyboardButton("Shortener",callback_data="admin:shortener")],
        [InlineKeyboardButton("Premium",callback_data="admin:premium")],
        [InlineKeyboardButton("Auto Delete",callback_data="admin:delete"),InlineKeyboardButton("Protection",callback_data="admin:protect")],
        [InlineKeyboardButton("Statistics",callback_data="admin:stats")]])
    await message.reply_text("Admin Settings",reply_markup=keyboard)
