from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import DB_NAME
from utils.database import Database
from states.admin_state import CategoryState
from keyboards.admin_inline_keyboards import make_categories_kb, make_confirm_kb

category_router = Router()
db = Database(DB_NAME)


@category_router.message(Command('categories'))
async def category_list_handler(message: Message):

    await message.answer(
        text="All categories:",
        reply_markup=make_categories_kb()
    )


@category_router.message(Command('add_category'))
async def category_add_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryState.addCategoryState)
    await message.answer(text="Please, send new category...")


@category_router.message(CategoryState.addCategoryState)
async def add_insert_handler(message: Message, state: FSMContext):
    if db.check_category_exists(message.text):
        if db.add_categories(new_category=message.text):
            await state.clear()
            await message.answer(f"New category by name {message.text} successfully added!")
        else:
            await message.answer(
                "Something was wrong, resend later\n"
                f"Send other name or click /cancel to cancel process"
            )
    else:
        await message.answer(
            f"Category \{message.text}\ already exists!\n"
            f"Send other name or click /cancel to cancel process"
        )


@category_router.message(Command('edit_category'))
async def category_edit_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryState.startCategoryState)
    await message.answer(
        text="Select category to edit...:",
        reply_markup=make_categories_kb()
    )


@category_router.callback_query(CategoryState.startCategoryState)
async def select_category_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CategoryState.finishCategoryState)
    await state.update_data(cat_name=callback.data)
    await callback.message.edit_text(f"Please, send new name for category {callback.data}")


@category_router.message(CategoryState.finishCategoryState)
async def update_category_handler(message: Message, state: FSMContext):
    if db.check_category_exists(message.text):
        all_data = await state.get_data()
        if db.rename_categories(old_name=all_data.get('cat_name'), new_name=message.text):
            await state.clear()
            await message.answer(f"Category name successfully modified!")
    else:
        await message.answer(
            f"Category \"{message.text}\" already exists!\n"
            f"Send other name or click /cancel to cancel process"
        )


@category_router.message(Command('del_category'))
async def category_del_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryState.startDeleteState)
    await message.answer(
        text="Select category to delete:",
        reply_markup=make_categories_kb()
    )


@category_router.callback_query(CategoryState.startDeleteState)
async def select_category_del_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CategoryState.finishDeleteState)
    await state.update_data(cat_name=callback.data)
    await callback.message.edit_text(
        text=f"Do you want to delete category {callback.data}",
        reply_markup=make_confirm_kb()
    )


@category_router.callback_query(CategoryState.finishDeleteState)
async def remove_category_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'YES':
        all_data = await state.get_data()
        if db.delete_categories(all_data.get('cat_name')):
            await callback.message.delete()
            await callback.message.answer("Category successfully deleted!")
            await state.clear()
        else:
            await callback.message.answer(
                f"Something went wrong!\n"
                f"Try again later or click /cancel to cancel process"
            )
    else:
        await state.clear()
        await callback.message.answer("Process cancelled!")
        await callback.message.delete()