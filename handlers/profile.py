from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.user_model import get_user_by_id
from telegram.constants import ParseMode

async def menu_profil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    user_data = get_user_by_id(user_id)
    if not user_data:
        await query.edit_message_text("❌ Profil tidak ditemukan.")
        return

    alias = user_data[2]
    if not alias:
        await query.edit_message_text("❌ Alias kamu belum diatur. Silakan atur alias dulu.")
        return

    bot_username = context.bot.username or "your_bot"
    link = f"https://t.me/{bot_username}?start={alias}-{user_id}"

    keyboard = [
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="menu_kembali"),
            InlineKeyboardButton("✏️ Ganti Alias", callback_data="ganti_alias"),
        ]
    ]

    await query.edit_message_text(
        f"<b>👤 Profil Kamu</b>\n\n"
        f"• Alias: <b>{alias}</b>\n"
        f"• Link Rahasia:\n<code>{link}</code>\n\n"
        f"🔗 Bagikan link ini ke temanmu supaya mereka bisa kirim pesan anonim 💌",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
