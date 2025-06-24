# --- admin_alias_search.py ---
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ParseMode
from datetime import datetime

from models.message_model import get_messages_by_user_id
from models.user_model import get_user_by_alias

# State
CARI_ALIAS = 1

# 🔍 Mulai pencarian berdasarkan alias
async def start_search_alias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()  # bersihkan state lama
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔎 Masukkan alias yang ingin dicari:")
    return CARI_ALIAS

# ✅ Tampilkan hasil pencarian alias
async def handle_search_alias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alias = update.message.text.strip()
    user_data = get_user_by_alias(alias)

    if not user_data:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Kembali ke Menu Admin", callback_data="admin_back_to_menu")]
        ])
        await update.message.reply_text("❌ Alias tidak ditemukan.", reply_markup=keyboard)
        return ConversationHandler.END

    user_id, username, alias = user_data

    messages = get_messages_by_user_id(user_id)
    msg_lines = [
        f"<b>👤 Detail Pengguna</b>",
        f"━━━━━━━━━━━━━━━━━━━━━",
        f"🆔 ID User: <code>{user_id}</code>",
        f"🔗 Username: @{username or 'Tidak ada'}",
        f"🏷️ Alias: <b>{alias}</b>",
        f"━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"<b>📥 Pesan Masuk:</b>",
    ]

    if not messages:
        msg_lines.append("❌ Belum ada pesan masuk.")
    else:
        for i, (sender_name, sender_username, sender_id, message, timestamp) in enumerate(messages, 1):
            waktu = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            msg_lines += [
                "",
                f"📨 <b>Pesan #{i}</b>",
                f"🧑 Dari: {sender_name}, @{sender_username or 'Tidak ada'} (ID: <code>{sender_id}</code>)",
                f"🕒 Waktu: {waktu}",
                f"💬 Pesan:",
                f"{message}"
            ]

    await update.message.reply_text(
        "\n".join(msg_lines[:4096]),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Kembali ke Menu Admin", callback_data="admin_back_to_menu")]
        ])
    )
    return ConversationHandler.END

# 🔁 Handler Conversation alias
alias_search_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_search_alias, pattern="^admin_search_alias$")],
    states={
        CARI_ALIAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_alias)],
    },
    fallbacks=[],
)
