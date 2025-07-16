from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from models.message_model import get_messages_for_user, save_message

# 🔽 Menu inbox (daftar pesan masuk user)
async def menu_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    messages = get_messages_for_user(user_id)

    if not messages:
        await query.edit_message_text("📬 Belum ada pesan anonim yang masuk.")
        return

    text = "<b>📥 Pesan Masuk Anonim:</b>\n\n"
    for i, (message, timestamp) in enumerate(messages, 1):
        text += (
            f"<b>📨 Pesan #{i}</b>\n"
            f"🕒 Waktu: {timestamp}\n"
            f"💬 <b>Pesan:</b>\n{message}\n\n"
        )

    await query.edit_message_text(text[:4096], parse_mode=ParseMode.HTML)

# 🔽 Step 1: User membuka link alias
async def handle_anon_entry(update: Update, context: ContextTypes.DEFAULT_TYPE, param: str):
    if "-" not in param:
        await update.message.reply_text("❌ Link tidak valid.")
        return

    alias, user_id_str = param.split("-", 1)
    if not user_id_str.isdigit():
        await update.message.reply_text("❌ Link rusak.")
        return

    context.user_data["target_user_id"] = int(user_id_str)
    context.user_data["alias"] = alias

    await update.message.reply_text(
        "📝 Tulis pesan anonim kamu di sini. Kami akan mengirimkannya secara rahasia ke target!",
        parse_mode=ParseMode.HTML
    )

# 🔽 Step 2: Simpan & kirim pesan anonim ke target
async def handle_anon_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    target_user_id = context.user_data.get("target_user_id")
    alias = context.user_data.get("alias", "tidak diketahui")
    message_text = update.message.text.strip()

    if not target_user_id:
        await update.message.reply_text("❌ Tidak ada tujuan pesan.")
        return

    if not message_text:
        await update.message.reply_text("❌ Pesan tidak boleh kosong.")
        return

    # Simpan pesan ke database
    save_message(
        target_user_id=target_user_id,
        sender_user_id=sender.id,
        sender_username=sender.username or "TanpaUsername",
        sender_name=sender.full_name or "TanpaNama",
        message=message_text
    )

    # Konfirmasi ke pengirim
    await update.message.reply_text(
        "✅ Pesanmu sudah terkirim secara anonim. Makasih ya!",
        parse_mode=ParseMode.HTML
    )

    # Kirim pesan ke target dengan tombol LAPORKAN
    try:
        cleaned_message = message_text.replace("\n", " ")[:30]
        callback = f"report_{sender.full_name or 'TanpaNama'}|{sender.username or 'TanpaUsername'}|{sender.id}|{cleaned_message}"

        pesan_anonim = f"📩 <b>Kamu dapat pesan anonim baru:</b>\n\n{message_text}"
        tombol_lapor = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚨 Laporkan", callback_data=callback)]
        ])

        await context.bot.send_message(
            chat_id=target_user_id,
            text=pesan_anonim,
            reply_markup=tombol_lapor,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(f"[ERROR] Gagal kirim pesan ke target user: {e}")
