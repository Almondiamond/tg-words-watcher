from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from dotenv import dotenv_values

import kb
from states import Gen

router = Router()

words_watching = []

OWNER_ID = dotenv_values(".env").get('OWNER_ID')


class RestrictToOwner(Filter):
    def __init__(self, owner_id: int) -> None:
        self.owner_id = owner_id

    async def __call__(self, message: Message) -> bool:
        condition = str(message.from_user.id) == str(self.owner_id)
        return condition


start_message = ('Привет. Я помогу тебе отслеживать интересные сообщения. '
                 'Просто скажи мне, какие слова тебя интересуют и добавляй в нужную группу, '
                 'а я буду пересылать тебе нужные сообщения. '
                 'PS: я нечувствителен к регистру')

new_tracking_word_message = 'Хорошо, теперь отслеживаю слово {0}'

word_removed_message = 'Слово {0} больше не отслеживается'


@router.message(RestrictToOwner(OWNER_ID), Command('start'))
async def start_handler(msg: Message):
    await msg.answer(
        start_message,
        reply_markup=kb.menu
    )


@router.callback_query(F.data == 'words_list')
async def show_words_list(callback_query: CallbackQuery):
    if len(words_watching) > 0:
        await callback_query.message.edit_text(
            'Сейчас отслеживаются слова: ' + ', '.join(words_watching),
            reply_markup=kb.words_tracking
        )
        return
    await callback_query.message.edit_text(
        'Пока что ничего не отслеживается. Самое время что-нибудь добавить!',
        reply_markup=kb.words_tracking
    )


@router.callback_query(F.data == 'words_add')
async def add_word_prompt(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.add_word_prompt)
    await callback_query.message.edit_text(
        'Напиши мне какое слово отслеживать..',
        reply_markup=kb.exit
    )


@router.message(Gen.add_word_prompt)
async def new_word_added(msg: Message, state: FSMContext):
    prompt = msg.text
    if not (prompt in words_watching):
        words_watching.append(prompt)
    await state.clear()
    await msg.answer(
        new_tracking_word_message.format(prompt.lower()),
        reply_markup=kb.menu
    )


@router.callback_query(F.data == 'words_delete')
async def delete_word_prompt(callback_query: CallbackQuery, state: FSMContext):
    if len(words_watching) > 0:
        await state.set_state(Gen.delete_word_prompt)
        await callback_query.message.edit_text(
            'Какое слово ты хочешь удалить?',
            reply_markup=kb.exit
        )


@router.message(Gen.delete_word_prompt)
async def word_deleted(msg: Message, state: FSMContext):
    prompt = msg.text.lower()
    if prompt in words_watching:
        words_watching.remove(prompt)
    await state.clear()
    await msg.answer(
        word_removed_message.format(prompt),
        reply_markup=kb.menu
    )


@router.callback_query(F.data == 'menu')
async def back_to_menu(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text(
        start_message,
        reply_markup=kb.menu
    )


@router.message()
async def message_handler(msg: Message):
    if msg.chat.type == 'private':
        if str(msg.from_user.id) != str(OWNER_ID):
            await msg.answer("Я работаю, но мне запретили с тобой общаться, извини.")
        else:
            await msg.answer(
                'Я тебя не понял. Лучше нажимай кнопочки ниже.',
                reply_markup=kb.menu
            )

    elif msg.chat.type == 'group':
        words_to_watch_lowercase = [x.lower() for x in words_watching]
        words = [x.lower() for x in msg.text.split()]

        if any(w in words_to_watch_lowercase for w in words):
            await msg.forward(OWNER_ID)
