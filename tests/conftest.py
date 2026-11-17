"""Shared test setup: every test run uses its own throwaway SQLite file."""
import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="tutor-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
# Nothing listens here, so the Neo4j client fails fast instead of waiting on a real server.
os.environ["NEO4J_URI"] = "bolt://127.0.0.1:1"
# No real model in tests: the LLM seam answers with canned text.
os.environ["TUTOR_LLM"] = "fake"
