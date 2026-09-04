from backend.matcher import ResumeMatcher

def test_clean():
    assert ResumeMatcher.clean("  Python\n FASTAPI ") == "python fastapi"
