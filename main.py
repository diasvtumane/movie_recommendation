import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from recommender import MovieRecommender
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CLOUD_RUN_SERVICE_URL = os.getenv("CLOUD_RUN_SERVICE_URL")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set.")
if not CLOUD_RUN_SERVICE_URL:
    raise ValueError("CLOUD_RUN_SERVICE_URL environment variable is not set.")

# Initialize the recommender
recommender = MovieRecommender('./data/movies.csv')
recommender.train()

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! Send me a movie title, and I'll recommend similar movies.")

async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    movie_title = update.message.text
    recommendations = recommender.recommend(movie_title)

    if isinstance(recommendations, list) and isinstance(recommendations[0], dict):  # If recommendations include links
        keyboard = []
        for rec in recommendations:
            keyboard.append([
                InlineKeyboardButton(text=rec['title'], url=rec['imdb_url']),
                InlineKeyboardButton(text="Get Related Movies", callback_data=rec['title'])
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Recommendations for '{movie_title}':", reply_markup=reply_markup)

    elif isinstance(recommendations, list):  # If it's a closest match suggestion
        response = "\n".join(recommendations)
        await update.message.reply_text(f"Recommendations for '{movie_title}':\n{response}")

    else:
        await update.message.reply_text("Unexpected error occurred!")

async def related_movies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    movie_title = query.data
    recommendations = recommender.recommend(movie_title)

    if isinstance(recommendations, list) and isinstance(recommendations[0], dict):
        response = "\n".join([f"{rec['title']} - {rec['imdb_url']}" for rec in recommendations])
    else:
        response = "No related movies found."

    await query.edit_message_text(f"Related movies for '{movie_title}':\n{response}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Oops! Something went wrong. Please try again.")

# Main function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recommend))
    app.add_handler(CallbackQueryHandler(related_movies))

    # Use the PORT environment variable set by Cloud Run
    port = int(os.environ.get("PORT", 8080))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{CLOUD_RUN_SERVICE_URL}/webhook",
    )

if __name__ == "__main__":
    main()