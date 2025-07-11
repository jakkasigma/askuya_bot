from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from models.user_model import get_user_by_id, add_user
from handlers.user_menu import show_user_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username
    args = context.args

    # Jika /start dari link (berarti pengirim pesan anonim)
    if args:
        param = args[0]

        # Format: alias-userid (contoh: virgi-123456789)
        if '-' in param:
            alias_part, user_id_part = param.split('-', 1)
            if user_id_part.isdigit():
                from handlers.inbox import handle_anon_entry
                return await handle_anon_entry(update, context, f"{alias_part}-{user_id_part}")

        # Format tidak valid
        await update.message.reply_text("❌ Link tidak valid atau rusak.", parse_mode=ParseMode.HTML)
        return

    # Start biasa (user utama)
    user_data = get_user_by_id(user_id)

    if not user_data:
        # Tambahkan ke database
        add_user(user_id, username)
        await update.message.reply_text(
            "👋 <b>Hai! Sebelum lanjut, tulis nama alias kamu dulu ya:</b>\n\nContoh: <i>jakkaGanteng</i>",
            parse_mode=ParseMode.HTML
        )
        return

    if not user_data[2]:  # Cek apakah alias kosong
        await update.message.reply_text(
            "⚠️ <b>Kamu belum punya alias, tulis dulu ya:</b>\n\nContoh: <i>IrgiManis</i>",
            parse_mode=ParseMode.HTML
        )
        return

    # Jika sudah ada alias → langsung ke menu utama
    await show_user_menu(update, context)
