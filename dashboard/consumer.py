"""Kafka consumer that validates messages and writes valid events to Postgres."""
# Enabling workflows
from os import environ
import logging
import json
import time
import argparse
from datetime import datetime, time as dtime, timezone

from dotenv import load_dotenv
from confluent_kafka import Consumer, KafkaException, KafkaError
import psycopg2


logger = logging.getLogger(__name__)


def _parse_int_field(obj: dict, key: str):
    """Parse an field that may arrive as int or numeric string."""
    v = obj.get(key)

    if isinstance(v, bool):
        return False, None, f"'{key}' must be an integer"

    if isinstance(v, int):
        return True, v, ""

    if isinstance(v, str):
        s = v.strip()
        digits = s[1:] if s.startswith("-") else s
        if digits.isdigit():
            return True, int(s), ""
        return False, None, f"'{key}' must be an integer"

    return False, None, f"'{key}' must be an integer"


def _parse_iso_datetime(ts: str) -> datetime:
    """Parse timestamps that may arrive with a 'Z' suffix."""
    return datetime.fromisoformat(ts.strip().replace("Z", "+00:00"))


def _to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC for insertion into TIMESTAMP."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def _within_operating_hours(dt: datetime) -> bool:
    """
    Checks if the message falls within the valid window: 
    08:45 <= time <= 18:15 (inclusive).
    """
    start = dtime(8, 45)
    end = dtime(18, 15)
    t = dt.time()
    return start <= t <= end


def _validate_message(obj: object) -> tuple[bool, str]:
    """
    Checks if message arrives in an expected format.
    For example:
    {"at": "[timestamp]", "site": "[0-5]", "val": "[0-4 OR -1 IF 'type' exists]", "type": "[0-1]"}

    Where:
      - "type" optional.
      - if "type" exists -> "val" must be -1 and type in 0-1
      - if "type" absent -> "val" must be in 0-4
      - "site" in 0-5
      - "at" within 08:45–18:15 inclusive
    """
    if not isinstance(obj, dict):
        return False, "not a JSON object"

    for k in ("at", "site", "val"):
        if k not in obj:
            return False, f"missing '{k}'"

    at = obj.get("at")
    if not isinstance(at, str) or not at.strip():
        return False, "'at' must be a timestamp string"
    try:
        dt = _parse_iso_datetime(at)
    except ValueError:
        return False, "invalid 'at' timestamp (expected ISO-8601 format)"
    if not _within_operating_hours(dt):
        return False, "timestamp outside operating hours (08:45–18:15)"

    ok, site, reason = _parse_int_field(obj, "site")
    if not ok:
        return False, reason
    if site < 0 or site > 5:
        return False, "'site' out of range (0-5)"

    ok, val, reason = _parse_int_field(obj, "val")
    if not ok:
        return False, reason

    has_type = "type" in obj and obj.get("type") is not None
    if has_type:
        ok, t, reason = _parse_int_field(obj, "type")
        if not ok:
            return False, reason
        if t < 0 or t > 1:
            return False, "'type' out of range (0-1)"
        if val != -1:
            return False, "when 'type' exists, 'val' must be -1"
    else:
        if val < 0 or val > 4:
            return False, "when 'type' is absent, 'val' must be in 0-4"

    return True, ""


def _append_invalid(path: str, message_text: str, reason: str) -> None:
    """Appends an invalid message with the error reason to the error log file."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{message_text} | {reason}\n")


def _configure_logging(enabled: bool, log_path: str) -> None:
    """Handles logging settings"""
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    if not enabled:
        logging.disable(logging.CRITICAL)
        return

    logging.disable(logging.NOTSET)
    root.setLevel(logging.INFO)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(fh)


def _get_db_connection():
    """
    Connect to Postgres database
    """
    return psycopg2.connect(
        host=environ["DB_HOST"],
        port=environ["DB_PORT"],
        dbname=environ["DB_NAME"],
        user=environ["DB_USERNAME"],
        password=environ["DB_PASSWORD"]
    )


def _insert_interaction(cur, obj: dict) -> None:
    """
    Insert VALID messages:
      - rating_interaction when there is a rating value and no type
      - request_interaction when there is a type value
    Mapping:
      exhibition_id <- site
      event_at      <- at
      rating_id     <- val
      request_id    <- type
    """
    dt = _to_utc(_parse_iso_datetime(obj["at"]))
    ok, site, _ = _parse_int_field(obj, "site")
    if not ok:
        return

    if "type" in obj and obj.get("type") is not None:
        ok, req_id, _ = _parse_int_field(obj, "type")
        if not ok:
            return
        cur.execute(
            "INSERT INTO request_interaction (exhibition_id, request_id, event_at) VALUES (%s, %s, %s)",
            (site, req_id, dt),
        )
    else:
        ok, rating_id, _ = _parse_int_field(obj, "val")
        if not ok:
            return
        cur.execute(
            "INSERT INTO rating_interaction (exhibition_id, rating_id, event_at) VALUES (%s, %s, %s)",
            (site, rating_id, dt),
        )


def consume_messages(
    consumer: Consumer,
    topic: str,
    conn,
    logging_enabled: bool,
    invalid_path: str,
) -> None:
    consumer.subscribe([topic])

    last_activity = time.time()
    inserts_since_commit = 0

    cur = conn.cursor()
    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                if (not logging_enabled) and (time.time() - last_activity >= 60):
                    print("No messages yet (still polling)...", flush=True)
                    last_activity = time.time()
                continue

            last_activity = time.time()

            if msg.error() is not None:
                err = msg.error()
                if err.code() == KafkaError._PARTITION_EOF:
                    continue
                if logging_enabled:
                    logger.error("Kafka error: %s", err)
                else:
                    print(f"Kafka error: {err}", flush=True)
                continue

            raw = msg.value()
            text = raw.decode(
                "utf-8", errors="replace") if isinstance(raw, (bytes, bytearray)) else str(raw)

            output = text
            invalid_reason = ""

            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as e:
                invalid_reason = f"not valid JSON ({e.msg})"
                if logging_enabled:
                    _append_invalid(invalid_path, text, invalid_reason)
                else:
                    output = f"{text} Invalid: {invalid_reason}"
                print(output, flush=True)
                continue

            ok, invalid_reason = _validate_message(parsed)
            if not ok:
                if logging_enabled:
                    _append_invalid(invalid_path, text, invalid_reason)
                else:
                    output = f"{text} Invalid: {invalid_reason}"
                print(output, flush=True)
                continue

            try:
                _insert_interaction(cur, parsed)
                inserts_since_commit += 1
                if inserts_since_commit >= 100:
                    conn.commit()
                    inserts_since_commit = 0
            except Exception as e:
                conn.rollback()
                reason = f"db insert failed ({type(e).__name__}: {e})"
                if logging_enabled:
                    _append_invalid(invalid_path, text, reason)
                    logger.exception(
                        "DB insert failed; message appended to invalid file.")
                else:
                    output = f"{text} Invalid: {reason}"

            print(output, flush=True)

    finally:
        if inserts_since_commit:
            conn.commit()
        cur.close()


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--enable-logging",
        action="store_true",
        help="Enable logging (disables terminal issue output; writes logs to file).",
    )
    parser.add_argument(
        "--log-file",
        default="consumer.log",
        help="Log file path used when --enable-logging is set.",
    )
    parser.add_argument(
        "--invalid-file",
        default="invalid_messages.txt",
        help="File path to append invalid message contents to when logging is enabled.",
    )
    args = parser.parse_args()

    _configure_logging(args.enable_logging, args.log_file)

    consumer = Consumer({
        "bootstrap.servers": environ["BOOTSTRAP_SERVERS"],
        "security.protocol": environ["SECURITY_PROTOCOL"],
        "sasl.mechanisms": environ["SASL_MECHANISM"],
        "sasl.username": environ["USERNAME"],
        "sasl.password": environ["PASSWORD"],
        "group.id": environ["GROUP_ID"],
        "auto.offset.reset": environ.get("AUTO_OFFSET", "latest"),
        "enable.auto.commit": True,
    })

    conn = _get_db_connection()
    try:
        consume_messages(
            consumer,
            environ["TOPIC"],
            conn,
            logging_enabled=args.enable_logging,
            invalid_path=args.invalid_file,
        )
    except KeyboardInterrupt:
        if args.enable_logging:
            logger.info("Interrupted by user (Ctrl+C).")
    finally:
        consumer.close()
        conn.close()
