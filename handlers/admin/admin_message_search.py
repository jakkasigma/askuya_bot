from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler,
    filters, CallbackQueryHandler
)
from telegram.constants import ParseMode

from models.user_model import get_user_by_alias
from models.message_model import search_messages_by_alias_and_keyword
from utils.helper import admin_back_button

# State
CARI_PESAN = 1
REPLY_TO_USER = 2

# 🔍 Step 1: Mulai pencarian
async def start_search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📌 Masukkan alias dan isi pesan yang ingin dicari (contoh: <code>alias|pesannya</code>):",
        parse_mode=ParseMode.HTML
    )
    return CARI_PESAN

# 🔍 Step 2: Proses pencarian pesan
async def handle_search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if '|' not in text:
        await update.message.reply_text(
            "❌ Format tidak valid. Gunakan format: <code>alias|pesannya</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_back_button()
        )
        return ConversationHandler.END

    alias, keyword = text.split('|', 1)
    alias = alias.strip()
    keyword = keyword.strip()

    user_data = get_user_by_alias(alias)
    if not user_data:
        await update.message.reply_text("❌ Alias tidak ditemukan.", reply_markup=admin_back_button())
        return ConversationHandler.END

    user_id, username, alias = user_data
    messages = search_messages_by_alias_and_keyword(user_id, keyword)

    if not messages:
        await update.message.reply_text("📭 Tidak ada pesan yang cocok ditemukan.", reply_markup=admin_back_button())
        return ConversationHandler.END

    # Tampilkan semua hasil pencarian
    for i, (sender_username, sender_id, message, timestamp, sender_name) in enumerate(messages, 1):
        reply_text = (
            f"<b>📨 Pesan #{i}</b>\n"
            f"👤 Dari: {sender_name or 'None'} <a href='https://t.me/{sender_username}'>@{sender_username}</a> "
            f"(ID: <code>{sender_id}</code>)\n"
            f"🎯 Untuk: <b>{alias}</b>\n"
            f"🆔 ID Alias: <code>{user_id}</code>\n"
            f"🕒 Waktu: {timestamp}\n"
            f"💬 <b>Pesan:</b>\n{message}"
        )

        # Simpan ke context agar bisa digunakan saat membalas
        context.user_data[f"reply_data_{sender_id}"] = {
            "reply_target": sender_id,
            "reply_alias": alias,
            "original_message": message,
        }

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Balas pengirim ini", callback_data=f"reply_to_{sender_id}")],
            [InlineKeyboardButton("⬅️ Kembali ke Menu Admin", callback_data="admin_back_to_menu")]
        ])
        await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    return REPLY_TO_USER

# ✍️ Step 3: Admin pilih siapa yang mau dibalas
async def start_reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    sender_id = int(query.data.split("_")[-1])
    data = context.user_data.get(f"reply_data_{sender_id}", {})

    context.user_data['reply_target'] = data.get("reply_target")
    context.user_data['reply_alias'] = data.get("reply_alias")
    context.user_data['original_message'] = data.get("original_message")

    await query.edit_message_text("✍️ Tulis pesan balasan kamu untuk pengirim ini:")
    return REPLY_TO_USER

# ✅ Step 4: Admin kirim balasan
async def handle_reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_target = context.user_data.get('reply_target')
    alias = context.user_data.get('reply_alias')
    original_message = context.user_data.get('original_message')
    reply_text = update.message.text.strip()

    if not reply_target:
        await update.message.reply_text("❌ Tidak ditemukan ID tujuan balasan.", reply_markup=admin_back_button())
        return ConversationHandler.END

    try:
        await context.bot.send_message(
            chat_id=reply_target,
            text=(
                "📩 <b>Kamu mendapat balasan dari Admin:</b>\n\n"
                f"📨 Pesanmu sebelumnya ke <b>{alias}</b>:\n"
                f"\"{original_message}\"\n\n"
                f"📝 Balasan Admin:\n{reply_text}"
            ),
            parse_mode=ParseMode.HTML
        )
        await update.message.reply_text("✅ Balasan berhasil dikirim.", reply_markup=admin_back_button())
    except Exception as e:
        print(f"[ERROR] Gagal kirim balasan: {e}")
        await update.message.reply_text("❌ Gagal mengirim balasan.", reply_markup=admin_back_button())

    return ConversationHandler.END

# ❌ Cancel handler
async def cancel_search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Pencarian dibatalkan.", reply_markup=admin_back_button())
    return ConversationHandler.END

# 📦 Daftar handler conversation
search_message_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_search_message, pattern="^admin_search_message$")],
    states={
        CARI_PESAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_message)],
        REPLY_TO_USER: [
            CallbackQueryHandler(start_reply_to_user, pattern=r"^reply_to_\d+$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_message)
        ],
    },
    fallbacks=[MessageHandler(filters.COMMAND, cancel_search_message)],
)
