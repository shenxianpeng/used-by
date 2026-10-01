"""Shared pytest fixtures."""

import socket

import pytest


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    """Fail fast if a test reaches the network instead of mocking requests."""

    def guard(*args, **kwargs):
        raise RuntimeError("tests must not access the network; mock requests.get")

    monkeypatch.setattr(socket.socket, "connect", guard)
