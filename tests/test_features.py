from backend.matcher import normalize_text

def test_clean():
    assert normalize_text("  Python\n FASTAPI ") == "python fastapi"
