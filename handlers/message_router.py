from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from models.user_model import get_user_by_id
from handlers.alias import set_alias_handler
from handlers.inbox import handle_anon_message

async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routing pesan teks berdasarkan status user."""
    if not update.message or not update.message.text:
        return  # Jangan diproses kalau bukan pesan teks biasa

    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip()

    # Ambil data user dari database
    user_data = get_user_by_id(user_id)

    # 1. Jika user belum punya alias → anggap sebagai user baru
    if user_data and not user_data[2]:
        return await set_alias_handler(update, context, pertama_kali=True)

    # 2. Jika user sedang dalam mode kirim pesan anonim
    if context.user_data.get("target_user_id"):
        return await handle_anon_message(update, context)

    # 3. Default: tidak dikenali
    await update.message.reply_text(
        "❌ Maaf, aku tidak tahu harus ngapain dengan pesan itu.\n"
        "Silakan gunakan tombol menu atau link anonim saja ya.",
        parse_mode=ParseMode.HTML
    )

