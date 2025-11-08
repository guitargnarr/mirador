#!/bin/bash
# mirador-core PyPI Publication Script
# Created: November 8, 2025

echo "🚀 Publishing mirador-core v2.0.0 to PyPI"
echo ""
echo "📋 Pre-flight checks:"
echo "  ✅ Package built: dist/mirador_core-2.0.0.tar.gz"
echo "  ✅ Wheel built: dist/mirador_core-2.0.0-py3-none-any.whl"
echo "  ✅ setup.py metadata updated (matthewdscott7@gmail.com, guitargnarr/mirador)"
echo ""

# Check if PyPI token is set
if [ -z "$TWINE_PASSWORD" ]; then
    echo "❌ PyPI token not found in environment"
    echo ""
    echo "Please set your PyPI token:"
    echo "  export TWINE_USERNAME=__token__"
    echo "  export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE"
    echo ""
    echo "Or create ~/.pypirc with:"
    echo "[pypi]"
    echo "username = __token__"
    echo "password = pypi-YOUR_TOKEN_HERE"
    echo ""
    exit 1
fi

echo "✅ PyPI credentials configured"
echo ""
echo "📦 Uploading to PyPI..."
echo ""

# Upload to PyPI
python3 -m twine upload dist/* --verbose

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! mirador-core v2.0.0 published to PyPI"
    echo ""
    echo "📦 Package URL: https://pypi.org/project/mirador-core/"
    echo "📥 Install with: pip install mirador-core"
    echo ""
    echo "🧪 Test installation:"
    echo "  pip install mirador-core"
    echo "  python3 -c 'import mirador_core; print(\"✅ mirador-core imported successfully!\")'"
    echo ""
else
    echo ""
    echo "❌ Upload failed. Check errors above."
    exit 1
fi
