# --- admin_export_csv.py ---
import csv
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ContextTypes, 
    CallbackQueryHandler, 
    ConversationHandler, 
    MessageHandler, 
    filters
)

from models.message_model import get_all_messages, get_messages_by_alias
from models.user_model import get_user_by_id, get_user_by_alias

ASK_ALIAS = 101

def admin_back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali ke Menu Admin", callback_data="admin_back_to_menu")]
    ])

# 📦 Ekspor semua pesan ke CSV
async def export_all_messages_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    messages = get_all_messages()

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"semua_pesan_{now}.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Nama Pengirim", "Username", "ID", "Pesan", "Waktu", "Alias Penerima"])

        for msg in messages:
            name, username, sender_id, message, timestamp, target_user_id = msg
            target_data = get_user_by_id(target_user_id)
            target_alias = target_data[2] if target_data and target_data[2] else "❓Tidak Diketahui"
            writer.writerow([name, username, sender_id, message, timestamp, target_alias])

    with open(filename, "rb") as f:
        await query.message.reply_document(
            document=InputFile(f, filename=os.path.basename(filename)),
            caption="📦 Berikut file semua pesan dalam format CSV.",
            reply_markup=admin_back_button(),
            parse_mode="HTML"
        )

    os.remove(filename)
 
# 🔁 Step 1: Mulai ekspor by alias
async def start_export_by_alias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        "🔍 <b>Masukkan alias yang ingin diekspor pesannya:</b>",
        parse_mode="HTML"
    )
    return ASK_ALIAS

# 🔁 Step 2: Terima alias dan ekspor
async def handle_export_by_alias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alias = update.message.text.strip()
    user_data = get_user_by_alias(alias)

    if not user_data:
        await update.message.reply_text(
            "❌ Alias tidak ditemukan.",
            reply_markup=admin_back_button(),
            parse_mode="HTML"
        )
        return ConversationHandler.END

    user_id = user_data[0]
    messages = get_messages_by_alias(user_id)

    if not messages:
        await update.message.reply_text(
            f"ℹ️ Tidak ada pesan untuk alias <b>{alias}</b>.",
            reply_markup=admin_back_button(),
            parse_mode="HTML"
        )
        return ConversationHandler.END

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pesan_{alias}_{now}.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Nama Pengirim", "Username", "ID", "Pesan", "Waktu"])
        for msg in messages:
            writer.writerow(msg)

    with open(filename, "rb") as f:
        await update.message.reply_document(
            document=InputFile(f, filename=os.path.basename(filename)),
            caption=f"📅 Pesan untuk alias <b>{alias}</b>",
            reply_markup=admin_back_button(),
            parse_mode="HTML"
        )

    os.remove(filename)
    return ConversationHandler.END

export_by_alias_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_export_by_alias, pattern="^admin_export_by_alias$")],
    states={
        ASK_ALIAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_export_by_alias)],
    },
    fallbacks=[],
)
 