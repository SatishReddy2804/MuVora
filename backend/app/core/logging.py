import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    # Suppress verbose TF logging
    logging.getLogger("tensorflow").setLevel(logging.ERROR)

logger = logging.getLogger("muvora")
