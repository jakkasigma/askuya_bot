from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)

from database.user_db import get_all_user_ids

ASK_MESSAGE, CONFIRM_SEND = range(2)

# 🚀 Mulai broadcast
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    admin_ids = context.bot_data.get("ADMIN_IDS", [])

    if user_id not in admin_ids:
        if update.message:
            await update.message.reply_text("❌ Kamu tidak punya izin untuk mengakses fitur ini.")
        elif update.callback_query:
            await update.callback_query.answer("❌ Tidak diizinkan.", show_alert=True)
        return ConversationHandler.END

    prompt = "📢 Silakan kirim <b>pesan broadcast</b> yang ingin kamu kirim ke semua pengguna:"
    if update.message:
        await update.message.reply_text(prompt, parse_mode=ParseMode.HTML)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(prompt, parse_mode=ParseMode.HTML)

    return ASK_MESSAGE

# ✏️ Admin kirim isi pesan
async def ask_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["broadcast_message"] = update.message.text

    keyboard = [
        [InlineKeyboardButton("✅ Kirim ke Semua", callback_data="send_broadcast")],
        [InlineKeyboardButton("❌ Batal", callback_data="cancel_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"<b>Konfirmasi Broadcast:</b>\n\n{update.message.text}",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    return CONFIRM_SEND

# ✅ Kirim ke semua user
async def confirm_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_broadcast":
        await query.edit_message_text("❌ Broadcast dibatalkan.")
        return ConversationHandler.END

    raw_message = context.user_data.get("broadcast_message")
    message = f"📢 <b>Pesan BrotKes</b>\n\n{raw_message}"

    user_ids = get_all_user_ids()
    success = 0
    failed = 0

    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
            success += 1
        except Exception:
            failed += 1

    await query.edit_message_text(
        f"✅ Broadcast selesai!\n\n"
        f"📤 Berhasil: {success} user\n"
        f"❌ Gagal: {failed} user"
    )
    return ConversationHandler.END

# ❌ Batal
async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        await update.message.reply_text("❌ Broadcast dibatalkan.")
    return ConversationHandler.END

# 🔗 Handler utama
def get_broadcast_handler(admin_ids):
    return ConversationHandler(
        entry_points=[
            CommandHandler("broadcast", start_broadcast),
            CallbackQueryHandler(start_broadcast, pattern="^admin_broadcast$"),
        ],
        states={
            ASK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_message)],
            CONFIRM_SEND: [CallbackQueryHandler(confirm_send, pattern="^(send_broadcast|cancel_broadcast)$")]
        },
        fallbacks=[CommandHandler("cancel", cancel_broadcast)],
        allow_reentry=True
    )
