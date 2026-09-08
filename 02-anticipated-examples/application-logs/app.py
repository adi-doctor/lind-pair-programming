import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


def configure_logging(log_dir: str = "logs", log_file: str = "app.log") -> logging.Logger:
    """Configures application-wide logging with file rotation and console output."""
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    # 1. Base logger configuration
    logger = logging.getLogger("InventoryApp")
    logger.setLevel(logging.DEBUG)  # Capture everything down to DEBUG

    # Prevent duplicate logs if handler setup runs multiple times
    if logger.handlers:
        return logger

    # 2. Define message format: [Timestamp] [Level] [Module:Line] - Message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 3. Rotating File Handler: Max 5 MB per file, keeps last 3 backups
    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 4. Console Handler: Shows INFO and higher to standard output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Attach handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Initialize logger
logger = configure_logging()


class InventoryService:
    """Service to handle stock management and operations."""

    def __init__(self) -> None:
        self.stock: dict[str, int] = {"apples": 15, "oranges": 4}
        logger.info("InventoryService initialized with %d items.", len(self.stock))

    def restock(self, item: str, quantity: int) -> None:
        if quantity <= 0:
            logger.warning("Invalid restock attempt: %s with quantity %d", item, quantity)
            return

        self.stock[item] = self.stock.get(item, 0) + quantity
        logger.info("Restocked '%s' (+%d). Current stock: %d", item, quantity, self.stock[item])

    def purchase(self, item: str, quantity: int) -> bool:
        logger.debug("Purchase request received: item=%s, quantity=%d", item, quantity)

        if item not in self.stock:
            logger.error("Purchase failed: Item '%s' does not exist in inventory.", item)
            return False

        if self.stock[item] < quantity:
            logger.warning(
                "Purchase declined: Insufficient stock for '%s' (Requested: %d, Available: %d)",
                item,
                quantity,
                self.stock[item],
            )
            return False

        self.stock[item] -= quantity
        logger.info("Purchased %d '%s'. Remaining stock: %d", quantity, item, self.stock[item])

        if self.stock[item] <= 2:
            logger.warning("Low stock alert for '%s': only %d remaining!", item, self.stock[item])

        return True

    def calculate_discount(self, price: float, discount_percent: float) -> Optional[float]:
        if discount_percent > 100 or discount_percent < 0:
            logger.warning(f"Discount {discount_percent}% is out of bounds [0-100]. Calculation aborted.")
            return None

        discounted = price * (1 - (discount_percent / 100))
        logger.debug("Calculated price: Base=%.2f, Disc=%.1f%% -> Final=%.2f", price, discount_percent, discounted)
        return discounted


def main() -> None:
    logger.info("=== Starting Inventory Application ===")

    service = InventoryService()

    # Normal operations
    service.restock("bananas", 20)
    service.purchase("apples", 5)

    # Edge cases triggering warnings and errors
    service.restock("oranges", -2)      # Warning: invalid amount
    service.purchase("grapes", 2)       # Error: unknown item
    service.purchase("oranges", 10)     # Warning: out of stock

    # Triggering an exception log with stack trace
    service.calculate_discount(50.0, 150.0)

    logger.info("=== Application run finished ===")


if __name__ == "__main__":
    main()