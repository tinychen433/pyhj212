"""Shared test configuration and fixtures."""

from __future__ import annotations

import pytest

from pyhj212.models.header import Header
from pyhj212.models.message import Message


@pytest.fixture
def sample_header() -> Header:
    """Create a standard test header."""
    return Header(
        qn="20260902083001000",
        cn="2011",
        pw="123456",
        mn="ST0001",
        st="32",
        flag="4",
        pno="1",
    )


@pytest.fixture
def sample_message(sample_header: Header) -> Message:
    """Create a standard test message."""
    return Message(
        header=sample_header,
        data="w01001-Rtd=12.5;w01002-Rtd=34.0",
    )
