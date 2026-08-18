import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANDING_DIR = os.path.join(BASE_DIR, "Automation", "Landing")
PROCESSED_DIR = os.path.join(BASE_DIR, "Automation", "Processed")

TAG_CLEAN = 'clean_records'
TAG_DEAD_LETTER = 'dead_letter'