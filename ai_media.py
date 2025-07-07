import os
import asyncio
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
VEO3_API_TOKEN = os.environ.get("VEO3_API_TOKEN")

async def generate_image(prompt: str) -> str:
    """
    Generate an image using Replicate API with Stable Diffusion.
    Returns the URL of the generated image.
    """
    if not REPLICATE_API_TOKEN:
        raise ValueError("REPLICATE_API_TOKEN is not set")

    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "db21e45d4a4f4b3a9a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a",  # Replace with current Stable Diffusion version ID
        "input": {
            "prompt": prompt
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        prediction = response.json()

        # Poll for prediction result
        prediction_url = prediction["urls"]["get"]
        while True:
            res = await client.get(prediction_url, headers=headers)
            res.raise_for_status()
            result = res.json()
            if result["status"] == "succeeded":
                return result["output"][0]
            elif result["status"] == "failed":
                raise RuntimeError("Image generation failed")
            await asyncio.sleep(1)

async def generate_video(prompt: str) -> str:
    """
    Generate a short video using Veo 3 API.
    Returns the URL of the generated video.
    """
    if not VEO3_API_TOKEN:
        raise ValueError("VEO3_API_TOKEN is not set")

    url = "https://api.veo.co/v1/videos/generate"
    headers = {
        "Authorization": f"Bearer {VEO3_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "duration": 10  # seconds
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        video_url = result.get("video_url")
        if not video_url:
            raise RuntimeError("Video generation failed or no video URL returned")
        return video_url

async def bild_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Bitte gib einen Prompt für das Bild an, z.B. /bild Ein futuristischer Samurai auf einem Neon-Motorrad")
        return

    prompt = " ".join(context.args)
    await update.message.reply_text("Generiere Bild...")

    try:
        image_url = await generate_image(prompt)
        await update.message.reply_photo(photo=image_url)
    except Exception as e:
        await update.message.reply_text(f"Fehler bei der Bildgenerierung: {e}")

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Bitte gib einen Prompt für das Video an, z.B. /video Ein futuristischer Samurai auf einem Neon-Motorrad")
        return

    prompt = " ".join(context.args)
    await update.message.reply_text("Generiere Video...")

    try:
        video_url = await generate_video(prompt)
        await update.message.reply_video(video=video_url)
    except Exception as e:
        await update.message.reply_text(f"Fehler bei der Videogenerierung: {e}")
