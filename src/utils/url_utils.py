from __future__ import annotations

from urllib.parse import urljoin, urlparse


def normalize_domain(domain: str) -> str:
    value = (domain or "").strip().lower()
    for prefix in ("https://", "http://"):
        if value.startswith(prefix):
            value = value[len(prefix) :]
    value = value.strip("/")
    if value.startswith("www."):
        value = value[4:]
    return value


def build_url(domain: str, path: str) -> str:
    base = f"https://{normalize_domain(domain)}"
    return urljoin(base, path)


def same_registered_domain(url: str, company_domain: str) -> bool:
    host = urlparse(url).netloc.lower()
    return normalize_domain(company_domain) in host
