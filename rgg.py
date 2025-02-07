import logging
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Replace with your Telegram bot token
TOKEN = "7966906235:AAGe1P7ap3SuwQWFfJh1P2pAi8qI0qcDQkM"

# Function to fetch the image from API
def fetch_image(prompt: str):
    base_url = "https://imgen.duck.mom/prompt/"
    encoded_prompt = requests.utils.quote(prompt)
    api_url = f"{base_url}{encoded_prompt}"

    try:
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200 and "image" in response.headers["Content-Type"]:
            return response.content  # Return image bytes
        else:
            return None
    except requests.RequestException as e:
        logger.error(f"Error fetching image: {e}")
        return None

# Function to add watermark and timestamp
def add_watermark(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 22)  # Use Arial font
    except IOError:
        font = ImageFont.load_default()  # Fallback font

    # Watermark text
    watermark_text = "@pyxuss"
    timestamp_text = datetime.now().strftime("%d %B %Y, %I:%M %p")

    # Position (bottom-right corner)
    width, height = image.size
    text_position = (width - 140, height - 35)
    time_position = (width - 160, height - 55)

    # Draw text on image
    draw.text(text_position, watermark_text, fill="white", font=font)
    draw.text(time_position, timestamp_text, fill="white", font=font)

    # Save to BytesIO
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    
    return output

# Start command
async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Generate Another Image", callback_data="generate")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to Pyxuss AI Image Generator! 🎨\n\n✨ Type anything, and I’ll create an AI-powered image for you instantly!"
    )

# Handle text prompts
async def handle_prompt(update: Update, context: CallbackContext):
    prompt = update.message.text

    await update.message.reply_text("✨ Generating your AI-powered image... Please wait.")

    # Fetch image
    image_data = fetch_image(prompt)

    if image_data:
        watermarked_image = add_watermark(image_data)

        keyboard = [[InlineKeyboardButton("Generate Another Image 🎨", callback_data="generate")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_photo(photo=watermarked_image)

        await update.message.reply_text(
            "🔥 **Enjoy your AI-generated image!** 🚀\n\n"
            "If you like this, share it and tag **@pyxuss** to support more AI creations!\n\n"
            "Want another image? Click below to generate more! ⬇️",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("❌ Image generation failed. Try again!")

# Handle inline button clicks
async def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "generate":
        await query.message.reply_text("✨ Type a new prompt to generate another AI image!")

# Main function to set up bot
def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))
    app.add_handler(MessageHandler(filters.Regex("Generate Another Image"), handle_prompt))
    app.add_handler(MessageHandler(filters.Regex("🎨"), handle_prompt))

    # Start the bot
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()