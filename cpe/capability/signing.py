"""Signature verification for the capability model (``17`` section 3 item 5, RC-62): the interface and the
Phase 1 double.

The production verifier checks the owner's signature over the whole capability tuple with the owner's public
key. That verifier, and every piece of key handling around it, is deferred with the secret-handling code of
item 5 (``17`` A0, OD10). Phase 1 verifies through the ``Verifier`` interface with ``HarnessVerifier``, a test
double owned by the harness in the way ``HarnessAnchorStore`` is: it holds no key material; its "signature" is a
digest bound to a signer identifier and to the exact canonical bytes, so that every mutation of a signed field,
every added or re-typed field and every other signer fails, while the same tuple serialised another way verifies.
It is not a cryptographic signature and never leaves the harness.
"""
from __future__ import annotations

import hmac
from dataclasses import dataclass
from typing import Protocol

from cpe.canonical import sha256_hex


class Verifier(Protocol):
    """Decides whether ``signature`` is the owner's signature over ``message``."""

    def verify(self, message: bytes, signature: str) -> bool: ...


@dataclass(frozen=True)
class HarnessVerifier:
    """The Phase 1 double: a digest over the signer identifier and the message, compared in constant time."""

    signer_id: str

    def sign(self, message: bytes) -> str:
        """Used by the harness only, to issue the capabilities the tests present."""
        return sha256_hex(b"cpe-harness-signature:" + self.signer_id.encode("utf-8") + b":" + message)

    def verify(self, message: bytes, signature: str) -> bool:
        return hmac.compare_digest(self.sign(message), signature)
