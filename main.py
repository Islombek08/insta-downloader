import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import instaloader

TOKEN = "8514377757:AAF0P9fLOjpeMfoGpIw4DJ7_GOAyE7oGV7c"

bot = Bot(token=TOKEN)
dp = Dispatcher()

L = instaloader.Instaloader(
    download_pictures=True,
    download_videos=True,
    save_metadata=False,
    compress_json=False
)

users = {}

# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📸 Instagram username yuboring (faqat public akkaunt):")

# Username qabul qilish
@dp.message(F.text)
async def get_username(message: types.Message):
    username = message.text.replace("@", "").strip()
    users[message.from_user.id] = username

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Postlar", callback_data="posts")],
        [InlineKeyboardButton(text="🎬 Reelslar", callback_data="reels")],
        [InlineKeyboardButton(text="🎥 Storylar", callback_data="stories")],
        [InlineKeyboardButton(text="⭐ Aktuallar", callback_data="highlights")]
    ])

    await message.answer(
        f"👤 @{username}\nNimani yuklaymiz?",
        reply_markup=kb
    )

# Tugmalarni ushlash
@dp.callback_query()
async def handle_buttons(call: types.CallbackQuery):
    user_id = call.from_user.id
    username = users.get(user_id)

    if not username:
        await call.message.answer("Avval username yuboring.")
        return

    await call.message.answer("⏳ Yuklanmoqda, iltimos kuting...")

    try:
        profile = instaloader.Profile.from_username(L.context, username)

        if call.data == "posts":
            await send_posts(call.message, profile)

        elif call.data == "reels":
            await send_reels(call.message, profile)

        elif call.data == "stories":
            await send_stories(call.message, profile)

        elif call.data == "highlights":
            await send_highlights(call.message, profile)

    except Exception as e:
        await call.message.answer("❌ Xatolik yoki akkaunt private.")
        print(e)

# 📸 Oddiy postlar (foto + video)
async def send_posts(message, profile):
    count = 0
    for post in profile.get_posts():
        if count == 3:
            break

        if post.is_video:
            await message.answer_video(post.video_url)
        else:
            await message.answer_photo(post.url)

        count += 1

# 🎬 Reelslar (faqat video)
async def send_reels(message, profile):
    count = 0
    found = False

    for post in profile.get_posts():
        if count == 5:
            break

        # Reels = video post
        if post.is_video and post.typename == "GraphVideo":
            await message.answer_video(post.video_url)
            count += 1
            found = True

    if not found:
        await message.answer("❌ Reels topilmadi.")

# 🎥 Storylar
async def send_stories(message, profile):
    stories = L.get_stories(userids=[profile.userid])
    sent = False

    for story in stories:
        for item in story.get_items():
            if item.is_video:
                await message.answer_video(item.video_url)
            else:
                await message.answer_photo(item.url)
            sent = True

    if not sent:
        await message.answer("❌ Story topilmadi yoki muddati o‘tgan.")

# ⭐ Aktuallar (Highlights)
async def send_highlights(message, profile):
    highlights = L.get_highlights(profile)
    sent = False

    for highlight in highlights:
        for item in highlight.get_items():
            if item.is_video:
                await message.answer_video(item.video_url)
            else:
                await message.answer_photo(item.url)
            sent = True
        break  # faqat 1 ta highlight

    if not sent:
        await message.answer("❌ Aktuallar topilmadi.")

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
