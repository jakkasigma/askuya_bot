from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram.constants import ParseMode
from models.user_model import get_user_by_id

# State untuk ConversationHandler
ASK_REPORT_REASON = 20

# Step 1: User klik tombol 'Laporkan'
async def ask_report_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_", 1)[-1]
    if data.count("|") < 3:
        await query.edit_message_text("❌ Format laporan tidak valid.")
        return ConversationHandler.END

    name, username, sender_user_id, original_message = data.split("|", 3)
    context.user_data["report_data"] = {
        "sender_id": sender_user_id,
        "sender_name": name,
        "sender_username": username,
        "original_message": original_message,
        "reporter_id": query.from_user.id
    }

    await query.edit_message_text("📝 Silakan tulis alasan kamu melaporkan pesan ini:")
    return ASK_REPORT_REASON

# Step 2: User menulis alasan laporan
async def handle_report_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reason = update.message.text.strip()
    data = context.user_data.get("report_data")

    if not data:
        await update.message.reply_text("❌ Data laporan tidak ditemukan.")
        return ConversationHandler.END

    alias_data = get_user_by_id(data["reporter_id"])
    alias = alias_data[2] if alias_data else "Tidak diketahui"

    report_text = (
        f"🚨 <b>PESAN LAPORAN dari {alias}</b>\n\n"
        f"🔍 <b>Identitas Pengirim:</b>\n"
        f"🧑 Nama: {data['sender_name']}\n"
        f"👤 Username: @{data['sender_username'] if data['sender_username'] else 'N/A'}\n"
        f"🆔 ID: <code>{data['sender_id']}</code>\n\n"
        f"💬 <b>Pesan yang Dikirim Oleh:</b>\n{data['original_message']}\n\n"
        f"✏️ <b>Isi Laporan:</b>\n{reason}"
    )

    admin_ids = context.bot_data.get("ADMIN_IDS", [])
    for admin_id in admin_ids:
        await context.bot.send_message(
            chat_id=admin_id,
            text=report_text,
            parse_mode=ParseMode.HTML
        )

    await update.message.reply_text("✅ Laporan kamu sudah dikirim ke admin. Terima kasih!")
    return ConversationHandler.END

# Handler utama untuk laporan
report_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(ask_report_reason, pattern=r"^report_")],
    states={
        ASK_REPORT_REASON: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report_reason)
        ],
    },
    fallbacks=[],
)
