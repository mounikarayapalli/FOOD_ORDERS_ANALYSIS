
from pathlib import Path

# Main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# CSV source file
CSV_FILE = PROJECT_ROOT / "food_orders.csv"

# Batch size
BATCH_SIZE = 100

# MySQL configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Mounika@2413"

# Raw database details
RAW_DATABASE = "food_orders_raw_db"
RAW_TABLE = "raw_food_orders"

ANALYTICS_DATABASE = "food_orders_analytics_db"
ANALYTICS_TABLE = "cleaned_food_orders"
