#!/usr/bin/env python3
"""Send generated SEO report files by email via SMTP."""

from __future__ import annotations

import argparse
import logging
import os
import smtplib
import ssl
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path


LOGGER = logging.getLogger("seo_report_email")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send daily SEO report files by email")
    parser.add_argument("--summary-file", default="output/daily_summary.md", help="Path to markdown summary file")
    parser.add_argument("--history-file", default="output/rank_history.csv", help="Path to cumulative history CSV")
    parser.add_argument("--daily-file", default="", help="Path to daily CSV snapshot (optional)")
    parser.add_argument(
        "--skip-if-missing",
        action="store_true",
        default=True,
        help="Exit 0 when summary file is missing (expected for non-target schedule runs)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would be sent without contacting SMTP server",
    )
    return parser.parse_args()


def setup_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def getenv_required(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def build_subject() -> str:
    date_str = datetime.now(timezone.utc).date().isoformat()
    prefix = os.getenv("REPORT_SUBJECT_PREFIX", "vainzof.co.il SEO")
    return f"{prefix} | Daily rank report | {date_str}"


def read_file(path: Path, required: bool) -> bytes | None:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Required file does not exist: {path}")
        return None
    return path.read_bytes()


def parse_recipients() -> list[str]:
    raw = getenv_required("SMTP_TO")
    recipients = [r.strip() for r in raw.split(",") if r.strip()]
    if not recipients:
        raise RuntimeError("SMTP_TO is empty after parsing recipients")
    return recipients


def add_attachment_if_exists(msg: EmailMessage, file_path: Path, mime: str) -> None:
    if not file_path.exists():
        LOGGER.warning("Attachment not found, skipping: %s", file_path)
        return

    data = file_path.read_bytes()
    maintype, subtype = mime.split("/", maxsplit=1)
    msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=file_path.name)


def send_email(msg: EmailMessage, host: str, port: int, username: str, password: str) -> None:
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context()) as server:
            server.login(username, password)
            server.send_message(msg)
        return

    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(username, password)
        server.send_message(msg)


def main() -> int:
    setup_logging()
    args = parse_args()

    summary_path = Path(args.summary_file)
    history_path = Path(args.history_file)
    daily_path = Path(args.daily_file) if args.daily_file else None

    if not summary_path.exists() and args.skip_if_missing:
        LOGGER.info("Summary file not found (%s). Skipping email send.", summary_path)
        return 0

    try:
        smtp_host = getenv_required("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = getenv_required("SMTP_USERNAME")
        smtp_password = getenv_required("SMTP_PASSWORD")
        smtp_from = getenv_required("SMTP_FROM")
        recipients = parse_recipients()

        summary_bytes = read_file(summary_path, required=True)
        summary_text = summary_bytes.decode("utf-8") if summary_bytes else ""

        msg = EmailMessage()
        msg["Subject"] = build_subject()
        msg["From"] = smtp_from
        msg["To"] = ", ".join(recipients)
        msg.set_content(
            "Daily SEO rank report is attached.\n\n"
            "Attached files:\n"
            "- daily_summary.md\n"
            "- rank_history.csv\n"
            "- daily rankings CSV (if produced)\n\n"
            "--- Daily Summary ---\n"
            f"{summary_text}"
        )

        add_attachment_if_exists(msg, summary_path, "text/markdown")
        add_attachment_if_exists(msg, history_path, "text/csv")
        if daily_path:
            add_attachment_if_exists(msg, daily_path, "text/csv")

        if args.dry_run:
            LOGGER.info("Dry run enabled. Would send to: %s", recipients)
            LOGGER.info("Subject: %s", msg["Subject"])
            return 0

        send_email(msg, smtp_host, smtp_port, smtp_username, smtp_password)
        LOGGER.info("Email sent successfully to %s recipient(s)", len(recipients))
        return 0
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("Failed to send email report: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
