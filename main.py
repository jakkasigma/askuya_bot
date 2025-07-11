import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from telegram import BotCommand
from database.db import init_db
from dotenv import load_dotenv
load_dotenv()


# ─────────────── 🔹 Handler Pengguna ───────────────
from handlers.start import start
from handlers.user_menu import show_user_menu, menu_bantuan
from handlers.profile import menu_profil
from handlers.inbox import menu_inbox
from handlers.alias import alias_conv_handler
from handlers.message_router import route_message

# ─────────────── 🔸 Handler Admin ───────────────
from handlers.admin.admin_menu import (
    admin_menu,
    show_all_users,
    show_all_messages_detailed,
    back_to_admin_menu,
)
from handlers.admin.admin_alias_search import alias_search_handler
from handlers.admin.admin_message_search import search_message_handler
from handlers.admin.admin_export_csv import (
    export_all_messages_csv,
    export_by_alias_handler,
)
from handlers.admin.admin_broadcast import get_broadcast_handler

# ─────────────── 🛡️ Handler Pelaporan ───────────────
from handlers.report import report_handler


def main():
    # Inisialisasi database
    init_db()

    # Ambil token bot & admin dari environment
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "").split(",")))
    MYSQLPORT = int(os.environ.get("MYSQLPORT", "3306"))
    print("🔐 BOT_TOKEN:", BOT_TOKEN)


    # Setup aplikasi Telegram
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.bot_data["ADMIN_IDS"] = ADMIN_IDS

    # 👤 Pengguna
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", menu_bantuan))
    application.add_handler(alias_conv_handler)
    application.add_handler(CallbackQueryHandler(menu_profil, pattern="^menu_profil$"))
    application.add_handler(CallbackQueryHandler(menu_inbox, pattern="^menu_inbox$"))
    application.add_handler(CallbackQueryHandler(show_user_menu, pattern="^menu_kembali$"))
    application.add_handler(CallbackQueryHandler(menu_bantuan, pattern="^menu_bantuan$"))

    # 👑 Admin
    application.add_handler(CommandHandler("admin", admin_menu))
    application.add_handler(alias_search_handler)
    application.add_handler(search_message_handler)
    application.add_handler(CallbackQueryHandler(show_all_users, pattern="^admin_all_users$"))
    application.add_handler(CallbackQueryHandler(show_all_messages_detailed, pattern="^admin_all_messages_detailed$"))
    application.add_handler(CallbackQueryHandler(back_to_admin_menu, pattern="^admin_back_to_menu$"))
    application.add_handler(CallbackQueryHandler(export_all_messages_csv, pattern="^admin_export_csv$"))
    application.add_handler(export_by_alias_handler)
    application.add_handler(get_broadcast_handler(ADMIN_IDS))

    # 🛡️ Pelaporan
    application.add_handler(report_handler)

    # 🔁 Pesan Umum
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))

    print("🚀 Bot aktif dan siap menerima pesan...")
    print("🔐 BOT_TOKEN:", BOT_TOKEN)
    print("🛡️ ADMIN_IDS:", ADMIN_IDS)

    application.run_polling()


if __name__ == "__main__":
    main()
