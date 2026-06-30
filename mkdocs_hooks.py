"""MkDocs build hook: переписывает относительные ссылки, выходящие за пределы
``docs/``, в абсолютные GitHub-URL.

Зачем: поддерживаемые доки (`docs/testing.md`, ADR и др.) ссылаются на код, CI и
корневые файлы репозитория относительными путями вида ``../backend/tests/`` или
``../../CHANGELOG.md``. На GitHub в файловом браузере такие ссылки работают, но в
сгенерированном MkDocs-сайте (где публикуется только ``docs/``) они ведут «в никуда».

Решение: на этапе сборки сайта такие ссылки заменяются на ссылки на сам репозиторий
(``blob`` для файлов, ``tree`` для каталогов). Исходные maintained-доки при этом не
меняются — относительные ссылки внутри ``docs/`` MkDocs резолвит сам.
"""
import posixpath
import re

_REPO = "https://github.com/ValekusVachpekus/pdn-control"
_BLOB = f"{_REPO}/blob/main/"
_TREE = f"{_REPO}/tree/main/"

# Маркдаун-ссылки и картинки: [label](target) и ![alt](target).
_LINK_RE = re.compile(r"(!?\[[^\]]*\])\(([^)\s]+)\)")
# Уже абсолютные схемы / якоря / mailto не трогаем.
_SKIP_RE = re.compile(r"^([a-z][a-z0-9+.-]*:|#|//|/)")


def _rewrite(page_dir: str, target: str) -> str:
    if _SKIP_RE.match(target):
        return target
    path, sep, anchor = target.partition("#")
    if path == "":
        return target  # чистый якорь на этой же странице
    # Резолвим относительно каталога страницы (в пределах docs/).
    norm = posixpath.normpath(posixpath.join(page_dir, path))
    if not norm.startswith(".."):
        return target  # ссылка остаётся внутри docs/ — MkDocs справится сам
    # Ссылка выходит за docs/ → переводим в путь от корня репозитория.
    repo_path = posixpath.normpath(posixpath.join("docs", page_dir, path))
    is_dir = target.endswith("/") or posixpath.splitext(repo_path)[1] == ""
    base = _TREE if is_dir else _BLOB
    return f"{base}{repo_path}{sep}{anchor}"


def on_page_markdown(markdown, page, config, files):
    page_dir = posixpath.dirname(page.file.src_uri)

    def repl(m):
        label, target = m.group(1), m.group(2)
        new_target = _rewrite(page_dir, target)
        return m.group(0) if new_target == target else f"{label}({new_target})"

    return _LINK_RE.sub(repl, markdown)
