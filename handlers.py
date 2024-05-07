from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from dotenv import dotenv_values

import kb
from models.word import Word
from states import Gen

router = Router()

OWNER_ID = dotenv_values(".env").get('OWNER_ID')

start_message = ('Привет. Я помогу тебе отслеживать интересные сообщения. '
                 'Просто скажи мне, какие слова тебя интересуют и добавляй в нужную группу, '
                 'а я буду пересылать тебе нужные сообщения. '
                 'PS: я нечувствителен к регистру')

new_tracking_word_message = 'Хорошо, теперь отслеживаю слово {0}'

word_removed_message = 'Слово {0} больше не отслеживается'


def words_to_strings(words: list[Word]) -> list[str]:
    return [word.content for word in words]


def get_user_words(user_id: int) -> list[Word]:
    return Word.select().where(Word.user_id == user_id)


@router.message(Command('start'))
async def start_handler(msg: Message):
    await msg.answer(
        start_message,
        reply_markup=kb.menu
    )


@router.callback_query(F.data == 'words_list')
async def show_words_list(callback_query: CallbackQuery):
    user_words: list[str] = words_to_strings(get_user_words(callback_query.from_user.id))
    if len(user_words) > 0:
        await callback_query.message.edit_text(
            'Сейчас отслеживаются слова: ' + ', '.join(user_words),
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
        'Какое слово добавить?',
        reply_markup=kb.exit
    )


@router.message(Gen.add_word_prompt)
async def new_word_added(msg: Message, state: FSMContext):
    prompt = msg.text
    user_words: list[Word] = Word.select().where(Word.user_id == msg.from_user.id)

    def get_text(word: Word) -> str:
        return word.content

    words_to_string = [get_text(x) for x in user_words]
    if not (prompt in words_to_string):
        Word.create(user_id=msg.from_user.id, content=prompt)
    await state.clear()
    await msg.answer(
        new_tracking_word_message.format(prompt.lower()),
        reply_markup=kb.menu
    )


@router.callback_query(F.data == 'words_delete')
async def delete_word_prompt(callback_query: CallbackQuery, state: FSMContext):
    if len(get_user_words(callback_query.from_user.id)) > 0:
        await state.set_state(Gen.delete_word_prompt)
        await callback_query.message.edit_text(
            'Какое слово ты хочешь удалить?',
            reply_markup=kb.exit
        )


@router.message(Gen.delete_word_prompt)
async def word_deleted(msg: Message, state: FSMContext):
    prompt = msg.text.lower()
    user_words: list[str] = words_to_strings(get_user_words(msg.from_user.id))
    if prompt in user_words:
        query = Word.delete().where(Word.user_id == msg.from_user.id, Word.content == prompt)
        query.execute()
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
    print(msg.from_user.id)
    print('OWNER_ID: ', OWNER_ID)
    if msg.chat.type == 'private':
        await msg.answer(
            'Я тебя не понял. Лучше нажимай кнопочки ниже.',
            reply_markup=kb.menu
        )

    elif msg.chat.type == 'group':
        words_watching = words_to_strings(get_user_words(msg.from_user.id))
        words_to_watch_lowercase = [x.lower() for x in words_watching[msg.from_user.id]]
        words = [x.lower() for x in msg.text.split()]

        if any(w in words_to_watch_lowercase for w in words):
            await msg.forward(OWNER_ID)
