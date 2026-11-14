"""USSD menu/flow handlers (state machine)."""

from __future__ import annotations

import logging

from django.conf import settings

from transfers.models import USSDSession

from .services import (
    SEND_DESTINATIONS,
    create_simulated_ussd_remittance,
    get_account_summary,
    get_destination_corridor,
    get_quote_for_corridor,
    get_send_destinations,
    get_transaction_status,
    has_recent_duplicate,
)
from .session import cancel_session, current_input, end_session, is_back, parse_text
from .validators import parse_amount_kes, parse_menu_choice, parse_reference, validate_amount_limits

logger = logging.getLogger(__name__)

WELCOME = (
    "Welcome to SwiftSend\n\n"
    "Send money across borders, easily.\n\n"
    "1. Send Money\n"
    "2. Exchange Rates\n"
    "3. Transaction Status\n"
    "4. My Account"
)

DEST_MENU_HEADER = "Where are you sending money?\n"


def con(text: str) -> dict:
    return {"type": "CON", "text": text}


def end(text: str) -> dict:
    return {"type": "END", "text": text}


def _destinations_menu():
    lines = [DEST_MENU_HEADER]
    for i, d in enumerate(SEND_DESTINATIONS, start=1):
        lines.append(f"{i}. {d['label']}")
    lines.append("0. Back")
    return "\n".join(lines)


def _destination_by_choice(choice: str):
    try:
        idx = int(choice)
    except (TypeError, ValueError):
        return None
    if 1 <= idx <= len(SEND_DESTINATIONS):
        return SEND_DESTINATIONS[idx - 1]
    return None


def handle(session: USSDSession, msisdn: str, text: str) -> dict:
    """Main dispatcher. Returns {'type': 'CON'|'END', 'text': str, ...meta}."""
    try:
        if session.metadata.get("expired_restart"):
            session.metadata.pop("expired_restart", None)
            session.state = "welcome"
            session.save(update_fields=["state", "metadata", "updated_at"])
            return con("Session restarted.\n\n" + WELCOME)

        parts = parse_text(text)
        state = session.state or "welcome"

        # Global: first dial
        if not parts:
            session.state = "welcome"
            session.metadata = session.metadata or {}
            session.save(update_fields=["state", "updated_at"])
            return con(WELCOME)

        # Allow explicit cancel at confirmation screen handled in state; generic safe exit
        # Back handling per-state below.
        if state == "welcome":
            return _handle_welcome(session, msisdn, parts)
        if state == "send_destination":
            return _handle_destination(session, parts)
        if state == "send_amount":
            return _handle_amount(session, parts)
        if state == "send_confirm":
            return _handle_confirm(session, msisdn, parts)
        if state == "rates_destination":
            return _handle_rates_destination(session, parts)
        if state == "status_ref":
            return _handle_status_ref(session, msisdn, parts)
        # Fallback to safe restart
        session.state = "welcome"
        session.metadata = {}
        session.save(update_fields=["state", "metadata", "updated_at"])
        return con(WELCOME)
    except Exception:
        logger.exception("USSD handler error session=%s", session.session_external_id)
        session.state = "error"
        end_session(session, USSDSession.Status.FAILED)
        return end("Sorry, we could not process your request. Please try again later.")


def _handle_welcome(session: USSDSession, msisdn: str, parts):
    choice = parse_menu_choice(parts[-1])
    if choice == "1":
        session.state = "send_destination"
        session.metadata = {}
        session.save(update_fields=["state", "metadata", "updated_at"])
        return con(_destinations_menu())
    if choice == "2":
        session.state = "rates_destination"
        session.metadata = {}
        session.save(update_fields=["state", "metadata", "updated_at"])
        return con("Exchange Rates\n\n" + _destinations_menu())
    if choice == "3":
        session.state = "status_ref"
        session.metadata = {}
        session.save(update_fields=["state", "metadata", "updated_at"])
        return con("Transaction Status\n\nEnter your transaction reference:")
    if choice == "4":
        return _handle_my_account(session, msisdn)
    return con("Invalid option.\n\n" + WELCOME)


def _handle_destination(session: USSDSession, parts):
    choice = parse_menu_choice(parts[-1])
    if is_back(choice):
        session.state = "welcome"
        session.metadata = {}
        session.save(update_fields=["state", "metadata", "updated_at"])
        return con(WELCOME)
    dest = _destination_by_choice(choice)
    if not dest:
        return con("Invalid selection.\n\n" + _destinations_menu())
    corridor = get_destination_corridor(dest["key"])
    if not corridor:
        # Retrieve from backend where possible; graceful if not configured.
        return con(
            f"{dest['label']} corridor is not available right now.\n\n" + _destinations_menu()
        )
    session.metadata = {**(session.metadata or {}), "destination": dest["key"], "destination_label": dest["label"], "corridor_code": corridor.code}
    session.state = "send_amount"
    session.save(update_fields=["state", "metadata", "updated_at"])
    return con(f"Send to {dest['label']}\n\nEnter amount to send (KES):")


def _handle_amount(session: USSDSession, parts):
    value = parse_menu_choice(parts[-1])
    if is_back(value):
        session.state = "send_destination"
        session.save(update_fields=["state", "updated_at"])
        return con(_destinations_menu())
    amount = parse_amount_kes(value)
    if amount is None:
        return con("Invalid amount. Enter a numeric amount in KES (e.g. 1000):")
    ok, err = validate_amount_limits(amount)
    if not ok:
        return con(f"{err}\n\nEnter amount to send (KES):")

    corridor = get_destination_corridor((session.metadata or {}).get("destination", ""))
    if not corridor:
        session.state = "send_destination"
        session.save(update_fields=["state", "updated_at"])
        return con("Selected corridor unavailable. Please choose again.\n\n" + _destinations_menu())
    try:
        quote = get_quote_for_corridor(corridor, amount)
    except Exception:
        logger.exception("Quote retrieval failed corridor=%s", corridor.code)
        return con("Unable to retrieve exchange rate now. Please try again later.\n\nEnter amount to send (KES):")

    session.metadata = {**(session.metadata or {}), "amount_kes": str(amount), "quote": quote, "corridor_code": corridor.code}
    session.state = "send_confirm"
    session.save(update_fields=["state", "metadata", "updated_at"])

    fee = quote.get("fee_amount", "0.00")
    summary = (
        "Confirm Transfer\n\n"
        f"Send: KES {quote.get('send_amount')}\n"
        f"To: {session.metadata.get('destination_label', corridor.receive_country)} ({quote.get('receive_currency')})\n"
        f"Rate: 1 KES = {quote.get('exchange_rate')} {quote.get('receive_currency')}\n"
        f"Fee: KES {fee}\n"
        f"Recipient gets: {quote.get('receive_amount')} {quote.get('receive_currency')}\n\n"
        "1. Confirm Transfer\n"
        "2. Cancel Transfer"
    )
    return con(summary)


def _handle_confirm(session: USSDSession, msisdn: str, parts):
    choice = parse_menu_choice(parts[-1])
    meta = session.metadata or {}
    if choice == "2" or choice.upper() == "CANCEL":
        cancel_session(session)
        return end("Transfer cancelled. Thank you for using SwiftSend.")
    if choice == "0":
        # treat as cancel/back out safely
        cancel_session(session)
        return end("Transfer cancelled. Thank you for using SwiftSend.")
    if choice != "1":
        return con("Invalid option.\n\n1. Confirm Transfer\n2. Cancel Transfer")

    if has_recent_duplicate(session):
        rem = session.remittance
        if rem:
            end_session(session, USSDSession.Status.COMPLETED)
            return end(_completion_message(rem))
        cancel_session(session)
        return end("This transaction could not be confirmed. Please try again.")

    corridor = get_destination_corridor(meta.get("destination", ""))
    amount = parse_amount_kes(meta.get("amount_kes"))
    if not corridor or amount is None:
        session.state = "welcome"
        session.metadata = {}
        session.save(update_fields=["state", "metadata", "updated_at"])
        return con("Session error. Please start again.\n\n" + WELCOME)

    remittance, _created = create_simulated_ussd_remittance(session=session, corridor=corridor, amount_kes=amount, msisdn=msisdn)
    session.remittance = remittance
    session.state = "completed"
    session.save(update_fields=["remittance", "state", "updated_at"])
    end_session(session, USSDSession.Status.COMPLETED)
    return end(_completion_message(remittance))


def _completion_message(remittance):
    demo = " (DEMO - no actual money movement)" if (remittance.metadata or {}).get("simulated") else ""
    return (
        f"Transaction submitted{demo}\n\n"
        f"Ref: {remittance.reference}\n"
        f"Amount: KES {remittance.send_amount}\n"
        f"To: {remittance.recipient_country} ({remittance.receive_currency})\n"
        f"Status: {remittance.status}\n\n"
        "Keep your reference for tracking."
    )


def _handle_rates_destination(session: USSDSession, parts):
    choice = parse_menu_choice(parts[-1])
    if is_back(choice):
        session.state = "welcome"
        session.metadata = {}
        session.save(update_fields=["state", "metadata", "updated_at"])
        return con(WELCOME)
    dest = _destination_by_choice(choice)
    if not dest:
        return con("Invalid selection.\n\n" + _destinations_menu())
    corridor = get_destination_corridor(dest["key"])
    if not corridor:
        return con(f"{dest['label']} exchange rate unavailable now.\n\n0. Back")
    # Show current rate (from backend corridor config/service) - no hardcoded production rates.
    msg = (
        f"Exchange Rate\n\n"
        f"KE (KES) to {dest['label']} ({corridor.receive_currency})\n"
        f"Rate: 1 KES = {corridor.exchange_rate} {corridor.receive_currency}\n"
        f"Fee: KES {corridor.fee_flat} + {corridor.fee_percent}%\n\n"
        "0. Back"
    )
    # keep in rates state to allow back
    session.metadata = {**(session.metadata or {}), "rates_dest": dest["key"]}
    session.state = "rates_destination"
    session.save(update_fields=["state", "metadata", "updated_at"])
    # If they picked a dest (not 0) show rate and expect 0 for back; if they enter 0 handled above.
    # But on same input we should end with CON showing rate.
    return con(msg)


def _handle_status_ref(session: USSDSession, msisdn: str, parts):
    value = parse_menu_choice(parts[-1])
    if is_back(value):
        session.state = "welcome"
        session.metadata = {}
        session.save(update_fields=["state", "metadata", "updated_at"])
        return con(WELCOME)
    ref = parse_reference(value)
    if not ref:
        return con("Invalid reference. Enter your transaction reference:\n(0. Back)")
    info = get_transaction_status(ref, msisdn)
    session.state = "welcome"
    session.metadata = {}
    end_session(session, USSDSession.Status.COMPLETED)
    if not info:
        return end("Transaction not found. Check the reference and try again.")
    demo = " (DEMO)" if info.get("is_demo") else ""
    return end(
        f"Transaction Status{demo}\n\n"
        f"Ref: {info['reference']}\n"
        f"Status: {info['status']}\n"
        f"Amount: {info['send_currency']} {info['send_amount']}\n"
        f"To: {info['destination']} ({info['receive_currency']} {info['receive_amount']})"
    )


def _handle_my_account(session: USSDSession, msisdn: str):
    summary = get_account_summary(msisdn or "")
    session.state = "welcome"
    session.metadata = {k: v for k, v in (session.metadata or {}).items() if k != "_msisdn"}
    end_session(session, USSDSession.Status.COMPLETED)
    if summary.get("found"):
        msg = (
            "My Account\n\n"
            f"Phone: {summary.get('masked_phone','')}\n"
            f"Name: {summary.get('name','User')}\n"
            f"Transactions: {summary.get('total_transactions',0)}\n"
        )
        if summary.get("last_reference"):
            msg += f"Last: {summary['last_reference']} ({summary.get('last_status','')})"
        else:
            msg += "Last: None"
        return end(msg)
    return end(
        "My Account\n\n"
        f"Phone: {summary.get('masked_phone','')}\n"
        "No verified account linked to this number."
    )
