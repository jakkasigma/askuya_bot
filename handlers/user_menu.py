from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.user_model import get_user_by_id
from telegram.constants import ParseMode
import logging

logger = logging.getLogger(__name__)

async def show_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_by_id(user_id)

    if not user_data:
        logger.warning(f"[USER MENU] Data user tidak ditemukan untuk user_id={user_id}")
        if update.message:
            await update.message.reply_text("❌ Data user tidak ditemukan.")
        elif update.callback_query:
            await update.callback_query.edit_message_text("❌ Data user tidak ditemukan.")
        return

    alias = user_data[2]

    keyboard = [
        [
            InlineKeyboardButton("📄 Profil", callback_data="menu_profil"),
            InlineKeyboardButton("📥 Inbox", callback_data="menu_inbox"),
            InlineKeyboardButton("❓ Bantuan", callback_data="menu_bantuan"),
        ]
    ]

    text = (
        f"Haii <b>{alias}</b> 👋\n"
        "Siap buat nerima pesan rahasia hari ini? 🤭\n\n"
        "Langsung aja pilih menu di bawah ini ya!"
    )

    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )

async def menu_bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pesan = (
        "<b>📖 Panduan Pengguna</b>\n\n"
        "Berikut beberapa hal yang bisa kamu lakukan di bot ini:\n\n"
        "🔹 <b>/start</b> – Mulai ulang bot dan tampilkan menu utama\n"
        "🔹 <b>✏️ Ganti Alias</b> – Ubah nama alias anonim kamu\n"
        "🔹 <b>📥 Inbox</b> – Cek pesan masuk dari link anonim\n"
        "🔹 <b>👤 Profil</b> – Lihat alias dan link profil kamu\n"
        "🔹 <b>/help</b> – Tampilkan pesan bantuan ini\n\n"
        "❗ Jika kamu menerima pesan yang tidak pantas, gunakan tombol <b>Laporkan</b> yang ada di bawah pesan tersebut."
    )

    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="menu_kembali")]]

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            pesan,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
    elif update.message:
        await update.message.reply_text(
            pesan,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
