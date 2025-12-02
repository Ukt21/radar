
import os
from dotenv import load_dotenv
import os

MEMPOOL_API_URL = os.getenv("MEMPOOL_API_URL")
WHALE_ADDRESSES = os.getenv("WHALE_ADDRESSES", "").split(",")

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MEMPOOL_API_URL = os.getenv("MEMPOOL_API_URL", "https://mempool.space/api")

# Список отслеживаемых BTC-кошельков китов
WHALE_ADDRESSES = [
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "1KE38bzdFVF1RG7EMD1N1JVPGhuxuTAFaw",
    "3Hki23XvZaDtsYHh7XvKDuU55EQo2Wb3m3",
    "bc1q8urxlm2uye3t6nwg0y44sn32p0ynvefxpqseu4",
    "bc1qwelntg7tpxwgmh7gea0kycclx87mksnvhaadgf",
    "bc1q8s3h3vw5xufdas890q29lpuca56r0ezqar0mvs",
    "bc1qx76pl3zzunj045tl0dhx36j2gpmw3mxt57l5un",
]
