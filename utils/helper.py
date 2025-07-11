from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def admin_back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali ke Menu Admin", callback_data="admin_back_to_menu")]
    ])