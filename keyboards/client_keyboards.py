from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import DB_NAME
from utils.database import Database

db = Database(DB_NAME)

next_prev_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅", callback_data="prev"),
            InlineKeyboardButton(text="➡", callback_data="next"),
        ]
    ]
)


def get_next_prev_keyboard(all_count, count=10, product_id=None):
    digits = []
    for i in range(count):
        digits.append(
            InlineKeyboardButton(
                text=str(i + 1), callback_data=str(i)
            )
        )

    over_digits = []
    if all_count > 10:
        for i in range(count):
            over_digits.append(
                InlineKeyboardButton(
                    text=str(i+1), callback_data=str(i)
                )
            )
        return InlineKeyboardMarkup(
            inline_keyboard=[
                over_digits,
                [
                    InlineKeyboardButton(text="⬅", callback_data="prev"),
                    InlineKeyboardButton(text="➡", callback_data="next"),
                ],
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[digits]
    )

