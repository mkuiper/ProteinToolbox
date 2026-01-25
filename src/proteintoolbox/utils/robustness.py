from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
import socket
import urllib.error

# Configure logging
logger = logging.getLogger(__name__)

def log_retry_attempt(retry_state):
    """Log retry attempts."""
    logger.warning(
        f"Retrying {retry_state.fn.__name__} due to {retry_state.outcome.exception()} "
        f"- Attempt {retry_state.attempt_number}"
    )

# Standard retry strategy for network operations
# Retries 3 times, waiting 1s, 2s, 4s...
# Catches standard network errors.
network_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((IOError, ConnectionError, TimeoutError, socket.timeout, urllib.error.URLError)),
    before_sleep=log_retry_attempt
)

# Standard retry strategy for flaky calculations
calculation_retry = retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=2),
    before_sleep=log_retry_attempt
)
