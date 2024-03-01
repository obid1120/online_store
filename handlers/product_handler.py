from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command

# from aiogram.fsm.state import

from config import DB_NAME
from keyboards.admin_inline_keyboards import categories_kb_4_products
from keyboards.client_keyboards import next_prev_kb, get_next_prev_keyboard
from states.admin_state import ProductState
from states.client_states import ShowStates
from utils.database import Database

product_router = Router()
db = Database(DB_NAME)


@product_router.message(Command('add_product'))
async def add_product_handler(message: Message, state: FSMContext):
    await state.set_state(ProductState.add_SelectCategoryProdState)
    await message.answer(
        text="Please choose a category to add product",
        reply_markup=categories_kb_4_products()
    )


@product_router.callback_query(ProductState.add_SelectCategoryProdState)
async def add_product_category_handler(query: CallbackQuery, state: FSMContext):
    await state.update_data(product_category=int(query.data))
    await state.set_state(ProductState.add_TitleProdState)
    await query.message.answer("Please, send title for your product...")
    await query.message.delete()


@product_router.message(ProductState.add_TitleProdState, )
async def add_product_title_handler(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(product_title=message.text)
        await state.set_state(ProductState.add_TextProdState)
        await message.answer("Please, send full description for your product: ")
    else:
        await message.answer("Please, send only text....")


@product_router.message(ProductState.add_TextProdState, )
async def add_product_text_handler(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(product_text=message.text)
        await state.set_state(ProductState.add_ImageProdState)
        await message.answer("Please, send photo for your product: ")
    else:
        await message.answer("Please, send only text....")


@product_router.message(ProductState.add_ImageProdState)
async def add_product_image_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(product_image=message.photo[-1].file_id)
        await state.set_state(ProductState.add_PriceProdState)
        await message.answer("Please, send price for your product: ")
    else:
        await message.answer("Please, send only photo....")


@product_router.message(ProductState.add_PriceProdState)
async def add_product_image_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(product_price=int(message.text))
        await state.set_state(ProductState.add_PhoneProdState)
        await message.answer("Please, send phone number for contact with you: ")
    else:
        await message.answer("Please, send only number....")


@product_router.message(ProductState.add_PhoneProdState)
async def add_product_contact_handler(message: Message, state: FSMContext):
    if message.text or message.contact:
        phone = message.text if message.text else message.contact.phone_number
        all_data = await state.get_data()
        # title, text, image, price, phone, cat_id, us_id
        result = db.add_product(
            title=all_data.get('product_title'),
            text=all_data.get('product_text'),
            image=all_data.get('product_image'),
            price=all_data.get('product_price'),
            phone=phone,
            cat_id=all_data.get('product_category'),
            us_id=message.from_user.id
        )
        if result:
            await message.answer("Your product successfully added!")
            product = db.get_last_product(message.from_user.id)
            # id, product_title, product_image, product_text, product_price, product_phone
            await message.answer_photo(
                photo=product[2],
                caption=f"<b>{product[1]}</b>\n\n{product[3]}\n\n<b>Pirce:</b> {product[4]}\n\n <b>Contact:</b> {product[5]}",
                parse_mode="HTML"
            )
        else:
            await message.answer("Something went wrong, please try again")
        await state.clear()
    else:
        await message.answer("Please, send contact or phone number....")


@product_router.message(Command('products'))
async def products_handler(message: Message, state: FSMContext):
    products = db.get_all_products()
    if products:
        if len(products) == 1:
            product = products[0]
            await message.answer_photo(
                photo=product[2],
                caption=f"<b>{product[1]}</b>\n\n{product[3]}\n\n<b>Price:</b> {product[4]}\n\n <b>Contact:</b> {product[5]}",
                parse_mode="HTML"
            )
        else:
            await state.set_state(ShowStates.showProductState)
            await state.update_data(index=0)
            await state.update_data(count=len(products))
            await state.update_data(product=products)
            product = products[0]
            await message.answer_photo(
                photo=product[2],
                caption=f"<b>{product[1]}</b>\n\n{product[3]}\n\n<b>Price:</b> {product[4]}\n\n <b>Contact:</b> {product[5]}",
                parse_mode="HTML",
                reply_markup=next_prev_kb
            )


@product_router.callback_query(ShowStates.showProductState)
async def show_product_callback_handler(query: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    index = all_data.get('index')
    count = all_data.get('count')
    products = all_data.get('product')
    # print(products)
    if query.data == "next":
        if index == count-1:
            index = 0
        else:
            index += 1
    else:
        if index == 0:
            index = count-1
        else:
            index -= 1

    await state.update_data(index=index)
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=products[index][2],
            caption=f"<b>{products[index][1]}</b>\n\n{products[index][3]}\n\n<b>Price:</b> {products[index][4]}\n\n <b>Contact:</b> {products[index][-1]}",
            parse_mode="HTML"
        ),
        reply_markup=next_prev_kb
    )

# ------------------------------------------------------------------------------


@product_router.message(Command('all_products'))
async def all_products_handler(message: Message, state: FSMContext):
    categories = db.get_categories()
    await state.set_state(ShowStates.showCategoryState)
    await message.answer(
        text=f"Please, select a category to view the products",
        reply_markup=categories_kb_4_products(),
        parse_mode="HTML"
    )


@product_router.callback_query(ShowStates.showCategoryState)
async def show_category_callback_query_handler(query: CallbackQuery, state: FSMContext):
    products = db.get_all_products(query.data)
    await state.set_state(ShowStates.showCategoryProductState)

    if products:
        count = len(products)
        page_count = int(count/5)+1 if count % 5 != 0 else int(count/5)
        product_packages = []

        for i in range(0, count, 5):
            product_package_slice = []
            for j in range(i, i+5):
                try:
                    product_package_slice.append(products[j])
                except IndexError:
                    break
            product_packages.append(product_package_slice)
        button_count = len(product_packages[0])

        print(product_packages)
        print(len(product_packages[0]))

        s = ""
        if count <= 10:
            for i in range(count):
                s += f"<b>{i+1}</b>. {products[i][1]}. <b>id</b: {products[i][0]}\n"
            kb = get_next_prev_keyboard(all_count=count, count=count)
            await query.message.answer(
                text=s, reply_markup=kb, parse_mode="HTML"
            )
            await query.message.delete()
        else:  # if count is more than 10, work the part
            await state.update_data(index=0)
            await state.update_data(product_count=count)
            await state.update_data(page_count=page_count)
            await state.update_data(product_packages=product_packages)
            # print(product_packages)
            for i in range(5):
                s += f"<b>{i+1}</b>. {products[i][1]}\n"
            kb = get_next_prev_keyboard(all_count=count, count=button_count)
            await query.message.answer(
                text=f"<b>Result:</b>\t {1}/{page_count}\n\n{s}", reply_markup=kb, parse_mode="HTML"
            )


@product_router.callback_query(ShowStates.showCategoryProductState)
async def show_category_product_callback_query_handler(query: CallbackQuery, state: FSMContext):
    if query.data == "next" or query.data == "prev":
        all_data = await state.get_data()
        page_index = all_data['index']
        count = all_data['product_count']
        page_count = all_data['page_count']
        product_packages = all_data['product_packages']

        if query.data == 'next':
            if page_index == page_count - 1:
                page_index = 0
            else:
                page_index += 1
        if query.data == 'prev':
            if page_index == 0:
                page_index = page_count - 1
            else:
                page_index -= 1

        s = ""

        for i in range(len(product_packages[page_index])):
            # print(product_packages[page_index])
            s += f"<b>{i+1}</b>. {product_packages[page_index][i][1]} id: {product_packages[page_index][i][0]}\n"

        kb = get_next_prev_keyboard(all_count=count, count=len(product_packages[page_index]))
        await state.update_data(index=page_index)
        await query.message.edit_text(
            text=f"<b>Result:</b>\t {page_index+1}/{page_count}\n\n{s}",
            reply_markup=kb,
            parse_mode="HTML"
        )
    else:
        # await state.set_state(ShowStates.showCategoryProductState)
        all_data = await state.get_data()
        page_index = all_data['index']
        product_packages = all_data['product_packages']

        s = (
            f"{product_packages[page_index][int(query.data)][1]}\n\n"
            f"{product_packages[page_index][int(query.data)][3]}\n\n"
            f"<b>Price:</b> {product_packages[page_index][int(query.data)][4]}\n"
            f"<b>Contact:</b> {product_packages[page_index][int(query.data)][5]}\n"
        )

        # print(product_packages[page_index][int(query.data)])
        await query.message.answer_photo(
            photo=product_packages[page_index][int(query.data)][2],
            caption=s,
            parse_mode="HTML"
        )