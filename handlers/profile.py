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
    link = f"https://t.me/{context.bot.username}?start={alias}-{user_id}"

    keyboard = [
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="menu_kembali"),
            InlineKeyboardButton("✏️ Ganti Alias", callback_data="ganti_alias"),
        ]
    ]

    await query.edit_message_text(
    f"<b>👤 Profil Kamu</b>\n\n"
    f"✨ Alias kamu: <b>{alias}</b>\n"
    f"🔗 Link rahasia kamu:\n<code>{link}</code>\n\n"
    f"Bagikan link ini ke teman-temanmu agar mereka bisa ngirim pesan secara anonim ke kamu 💌",
    reply_markup=InlineKeyboardMarkup(keyboard),
    parse_mode=ParseMode.HTML
)

