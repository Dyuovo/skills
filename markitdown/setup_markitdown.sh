#!/usr/bin/env bash
# setup_markitdown.sh — Install Microsoft MarkItDown with all optional dependencies
set -euo pipefail

echo "=== MarkItDown Skill Setup ==="
echo ""

echo "Installing markitdown[all] from PyPI ..."
pip install 'markitdown[all]' -q

echo ""
echo "=== Verifying installation ==="
python3 -c "
from markitdown import MarkItDown
md = MarkItDown()
print('MarkItDown installed successfully')
"

echo ""
echo "=== Setup complete! ==="
echo "Test with: python3 markitdown_tool.py --help"
