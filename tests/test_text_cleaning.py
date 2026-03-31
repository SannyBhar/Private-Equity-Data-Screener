from src.utils.text_cleaning import html_to_clean_text, keyword_flag, normalize_whitespace


def test_html_to_clean_text_removes_script_and_nav() -> None:
    html = """
    <html><head><title>Acme</title><script>var x=1</script></head>
    <body><nav>Menu</nav><main>Enterprise automation platform</main></body></html>
    """
    title, text = html_to_clean_text(html)
    assert title == "Acme"
    assert "var x" not in text
    assert "Menu" not in text
    assert "Enterprise automation platform" in text


def test_keyword_flag() -> None:
    assert keyword_flag("We provide enterprise workflow software", ["enterprise"]) == 1
    assert keyword_flag("No overlap", ["healthcare"]) == 0


def test_normalize_whitespace() -> None:
    assert normalize_whitespace("  hello   world\n\t  ") == "hello world"
