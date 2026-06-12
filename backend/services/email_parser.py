import email
import email.policy
import re
from email import message_from_string
from pathlib import Path


def parse_eml(file_path: str) -> dict:
    path = Path(file_path)
    raw = path.read_text(errors="replace")
    msg = message_from_string(raw, policy=email.policy.default)

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
            elif part.get_content_type() == "text/html" and not body:
                body = _strip_html(part.get_content())
    else:
        body = msg.get_content()

    return {
        "subject": msg.get("Subject", ""),
        "from": msg.get("From", ""),
        "to": msg.get("To", ""),
        "cc": msg.get("Cc", ""),
        "date": msg.get("Date", ""),
        "body": body[:5000],
        "message_id": msg.get("Message-ID", ""),
        "references": msg.get("References", ""),
    }


def parse_mbox(file_path: str, max_messages: int = 100) -> list[dict]:
    import mailbox
    mbox = mailbox.mbox(file_path)
    messages = []
    for i, msg in enumerate(mbox):
        if i >= max_messages:
            break
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode("utf-8", errors="replace")
                    break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="replace")

        messages.append({
            "subject": str(msg.get("Subject", "")),
            "from": str(msg.get("From", "")),
            "to": str(msg.get("To", "")),
            "date": str(msg.get("Date", "")),
            "body": body[:3000],
        })
    return messages


def extract_email_entities(parsed: dict) -> dict:
    entities = []
    relationships = []

    from_addr = _extract_email_address(parsed.get("from", ""))
    from_name = _extract_name(parsed.get("from", ""))

    if from_name:
        entities.append({"name": from_name, "label": "Person", "properties": {"email": from_addr}})

    to_field = parsed.get("to", "")
    for addr in to_field.split(","):
        addr = addr.strip()
        if addr:
            name = _extract_name(addr)
            email_addr = _extract_email_address(addr)
            if name:
                entities.append({"name": name, "label": "Person", "properties": {"email": email_addr}})
                if from_name:
                    relationships.append({
                        "from": from_name,
                        "to": name,
                        "type": "EMAILED",
                        "properties": {"subject": parsed.get("subject", ""), "date": parsed.get("date", "")},
                    })

    return {"entities": entities, "relationships": relationships}


def _extract_email_address(s: str) -> str:
    m = re.search(r'<([^>]+)>', s)
    if m:
        return m.group(1)
    m = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', s)
    return m.group(0) if m else s.strip()


def _extract_name(s: str) -> str:
    m = re.match(r'"?([^"<]+)"?\s*<', s)
    if m:
        return m.group(1).strip()
    if "@" not in s:
        return s.strip()
    return s.split("@")[0].replace(".", " ").title()


def _strip_html(html: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
