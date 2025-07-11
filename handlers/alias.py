from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
)
from telegram.constants import ParseMode

from models.user_model import (
    set_alias,
    get_user_by_id,
    alias_exists
)

from constants import GANTI_ALIAS


# 🔘 Ketika user klik tombol "✏️ Ganti Alias"
async def ganti_alias_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "✏️ <b>Kirim alias baru kamu, Kak:</b>\n\nContoh: <i>opet_cantik</i>",
        parse_mode=ParseMode.HTML
    )
    return GANTI_ALIAS


# ✅ Handler utama untuk menyimpan alias (baru atau ganti)
async def set_alias_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, pertama_kali=False):
    user = update.effective_user
    user_id = user.id
    alias = update.message.text.strip().lower()  # ubah ke huruf kecil

    # Validasi format alias
    if not alias or len(alias) > 32 or " " in alias or "-" in alias:
        await update.message.reply_text(
            "❌ <b>Alias tidak boleh kosong, mengandung spasi, '-' atau lebih dari 32 karakter.</b>",
            parse_mode=ParseMode.HTML
        )
        return GANTI_ALIAS  # ⬅️ tetap di dalam conversation

    if alias_exists(alias, exclude_user_id=user_id):
        await update.message.reply_text(
            "❌ <b>Alias ini sudah digunakan orang lain. Coba yang lain ya!</b>",
            parse_mode=ParseMode.HTML
        )
        return GANTI_ALIAS  # ⬅️ tetap di dalam conversation


    # Simpan ke database
    set_alias(user_id, alias)

    # Buat link untuk dibagikan
    link = f"https://t.me/{context.bot.username}?start={alias}-{user_id}"

    keyboard = [
        [InlineKeyboardButton("📥 Inbox", callback_data="menu_inbox")],
        [InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="menu_kembali")]
    ]

    # Buat pesan sukses
    judul = "🎉 <b>Alias kamu berhasil dibuat sebagai</b>" if pertama_kali else "✅ <b>Alias kamu telah diganti menjadi</b>"
    catatan = (
        "Selamat datang di dunia pesan anonim!\n\nAyo mulai bagi link ini ke teman-temanmu 👀"
        if pertama_kali else
        "Inbox kamu siap menanti pesan baru 💌"
    )
    pesan = (
        f"{judul} <i>{alias}</i>\n\n"
        f"<code>{link}</code>\n\n"
        f"{catatan}"
    )

    await update.message.reply_text(
        pesan,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

    return ConversationHandler.END


# 🔁 Handler dari tombol (ubah alias)
async def set_alias_from_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await set_alias_handler(update, context, pertama_kali=False)


# 🔁 Handler dari user baru (isi alias pertama kali)
async def set_alias_first_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_by_id(user_id)

    if user_data and not user_data[2]:  # Belum punya alias
        return await set_alias_handler(update, context, pertama_kali=True)

    return  # Sudah punya alias, tidak perlu isi lagi


# 📦 ConversationHandler untuk Ganti Alias
alias_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(ganti_alias_button, pattern="^ganti_alias$")],
    states={
        GANTI_ALIAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_alias_from_button)],
    },
    fallbacks=[],
    per_message=False,
)
