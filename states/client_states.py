from aiogram.fsm.state import State, StatesGroup


class ShowStates(StatesGroup):
    showProductState = State()

    showCategoryState = State()
    showCategoryProductState = State()
    showGetProductState = State()
