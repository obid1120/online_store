from aiogram.fsm.state import State, StatesGroup


class CategoryState(StatesGroup):
    addCategoryState = State()

    startCategoryState = State()
    finishCategoryState = State()

    startDeleteState = State()
    finishDeleteState = State()


class ProductState(StatesGroup):
    add_SelectCategoryProdState = State()
    add_TitleProdState = State()
    add_TextProdState = State()
    add_ImageProdState = State()
    add_PriceProdState = State()
    add_PhoneProdState = State()