from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from models.admin_model import get_all_users
from models.message_model import get_all_messages_detailed
from models.user_model import get_user_by_id

import logging
logger = logging.getLogger(__name__)

# 🔧 Menu utama admin
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_ids = context.bot_data.get("ADMIN_IDS", [])

    if user_id not in admin_ids:
        await update.effective_message.reply_text("❌ Kamu bukan admin.")
        logger.warning(f"[ADMIN BLOCKED] User {user_id} mencoba akses menu admin.")
        return

    logger.info(f"[ADMIN MENU] User {user_id} membuka menu admin.")

    keyboard = [
        [InlineKeyboardButton("👥 Semua User", callback_data="admin_all_users")],
        [InlineKeyboardButton("📩 Semua Pesan Detail", callback_data="admin_all_messages_detailed")],
        [InlineKeyboardButton("🔎 Cari Pesan by Alias", callback_data="admin_search_alias")],
        [InlineKeyboardButton("🔍 Cari Pesan + Isi", callback_data="admin_search_message")],
        [InlineKeyboardButton("📤 Ekspor Semua Pesan (CSV)", callback_data="admin_export_csv")],
        [InlineKeyboardButton("📤 Ekspor per Alias", callback_data="admin_export_by_alias")],
        [InlineKeyboardButton("📢 Broadcast Pesan", callback_data="admin_broadcast")]
    ]

    await update.effective_message.reply_text(
        "<b>👑 Menu Admin:</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

# 👥 Semua user
async def show_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    users = get_all_users()
    if not users:
        await query.edit_message_text("❌ Tidak ada pengguna yang ditemukan.")
        return

    text = "<b>📋 Daftar Pengguna:</b>\n\n"
    for i, (user_id, username, alias) in enumerate(users, 1):
        text += f"{i}. <b>{alias or 'Tanpa Alias'}</b> — @{username or 'TanpaUsername'} (ID: <code>{user_id}</code>)\n"

    await query.edit_message_text(
        text.strip()[:4096],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Kembali ke Menu Admin", callback_data="admin_back_to_menu")]
        ])
    )

# 📩 Semua pesan lengkap
async def show_all_messages_detailed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    messages = get_all_messages_detailed()
    if not messages:
        await query.edit_message_text("📭 Belum ada pesan yang masuk.")
        return

    output = "<b>📬 Semua Pesan Masuk:</b>\n\n"
    for i, msg in enumerate(messages, 1):
        sender_username, sender_id, target_id, message, timestamp, sender_name = msg
        target_user = get_user_by_id(target_id)
        alias = target_user[2] if target_user else "Tidak diketahui"

        output += (
            f"<b>📨 Pesan #{i}</b>\n"
            f"🧑 Dari: {sender_name or 'TanpaNama'}, @{sender_username or 'TanpaUsername'} (ID: <code>{sender_id}</code>)\n"
            f"🎯 Untuk: <b>{alias}</b>\n"
            f"🆔 ID Alias: <code>{target_id}</code>\n"
            f"🕒 Waktu: {timestamp}\n"
            f"💬 <b>Pesan:</b>\n{message}\n\n"
        )

    await query.edit_message_text(
        output[:4096],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Kembali ke Menu Admin", callback_data="admin_back_to_menu")]
        ])
    )

# 🔁 Kembali ke menu admin
async def back_to_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await admin_menu(update, context)
