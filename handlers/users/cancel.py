from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.default import main
from loader import dp


@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel action via /cancel command"""
    current_state = await state.get_state()
    if current_state is None:
        # User is not in any state, ignoring
        return
    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Отменено.',reply_markup= main.mainMenu)
