#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist/linux"
DEB_DIR="$PROJECT_ROOT/fast-youtrack-deb"
VERSION="1.0.0"  # TODO: Extract from project

echo -e "${BLUE}Creating Fast YouTrack .deb package...${NC}"

# Check if distribution exists
if [ ! -f "$DIST_DIR/fast-youtrack-app" ] || [ ! -f "$DIST_DIR/subdomain_picker" ]; then
    echo -e "${RED}Error: Distribution not found. Run ./dist-linux.sh first${NC}"
    exit 1
fi

# Clean up previous package build
rm -rf "$DEB_DIR"
mkdir -p "$DEB_DIR"

# Create debian package structure
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/doc/fast-youtrack"
mkdir -p "$DEB_DIR/usr/share/fast-youtrack"

# Copy executables
echo -e "${YELLOW}Copying application files...${NC}"
cp "$DIST_DIR/fast-youtrack-app" "$DEB_DIR/usr/share/fast-youtrack/"
cp "$DIST_DIR/subdomain_picker" "$DEB_DIR/usr/share/fast-youtrack/"
cp "$DIST_DIR/fast-youtrack" "$DEB_DIR/usr/share/fast-youtrack/"

# Create wrapper script in /usr/bin
cat > "$DEB_DIR/usr/bin/fast-youtrack" << 'EOF'
#!/bin/bash
# Fast YouTrack launcher wrapper
cd "$HOME/.local/share/fast-youtrack" || {
    echo "Creating Fast YouTrack user directory..."
    mkdir -p "$HOME/.local/share/fast-youtrack"
    cd "$HOME/.local/share/fast-youtrack"
}

# Always copy fresh files from system installation (force update)
rm -f fast-youtrack fast-youtrack-app subdomain_picker
cp /usr/share/fast-youtrack/fast-youtrack .
cp /usr/share/fast-youtrack/fast-youtrack-app .
cp /usr/share/fast-youtrack/subdomain_picker .
chmod +x fast-youtrack fast-youtrack-app subdomain_picker

# Run the application
exec ./fast-youtrack
EOF

chmod +x "$DEB_DIR/usr/bin/fast-youtrack"

# Create desktop entry
cat > "$DEB_DIR/usr/share/applications/fast-youtrack.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Fast YouTrack
Comment=Quick time entry for YouTrack issues
Exec=fast-youtrack
Icon=applications-office
Terminal=false
Categories=Office;ProjectManagement;Development;
StartupNotify=true
Keywords=youtrack;time;tracking;productivity;
EOF

# Create control file
cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: fast-youtrack
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Depends: python3-tk, python3 (>= 3.8)
Maintainer: KMRH47 <your-email@example.com>
Description: Fast time entry application for YouTrack
 Fast YouTrack is a cross-platform application for quickly adding
 spent time to YouTrack issues. Features include:
 .
  - GUI subdomain and passphrase selection
  - Encrypted token storage
  - Cross-platform compatibility
  - Minimal dependencies
Homepage: https://github.com/yourusername/fast-youtrack
EOF

# Create postinst script (runs after installation)
cat > "$DEB_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications
fi

echo "Fast YouTrack installed successfully!"
echo "You can now:"
echo "  - Run 'fast-youtrack' from terminal"
echo "  - Find 'Fast YouTrack' in your applications menu"
echo "  - User data will be stored in ~/.local/share/fast-youtrack/"

exit 0
EOF

chmod +x "$DEB_DIR/DEBIAN/postinst"

# Create prerm script (runs before removal)
cat > "$DEB_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

echo "Removing Fast YouTrack..."
echo "Note: User data in ~/.local/share/fast-youtrack/ will be preserved"

exit 0
EOF

chmod +x "$DEB_DIR/DEBIAN/prerm"

# Copy documentation
if [ -f "$PROJECT_ROOT/README.md" ]; then
    cp "$PROJECT_ROOT/README.md" "$DEB_DIR/usr/share/doc/fast-youtrack/"
fi

# Create changelog
cat > "$DEB_DIR/usr/share/doc/fast-youtrack/changelog" << EOF
fast-youtrack ($VERSION) stable; urgency=medium

  * Initial release
  * Cross-platform YouTrack time tracking
  * GUI subdomain selection
  * Encrypted token storage

 -- KMRH47 <your-email@example.com>  $(date -R)
EOF

# Compress changelog
gzip -9 "$DEB_DIR/usr/share/doc/fast-youtrack/changelog"

# Create copyright file
cat > "$DEB_DIR/usr/share/doc/fast-youtrack/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: fast-youtrack
Source: https://github.com/yourusername/fast-youtrack

Files: *
Copyright: $(date +%Y) KMRH47
License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
EOF

# Set proper permissions
find "$DEB_DIR" -type f -exec chmod 644 {} \;
find "$DEB_DIR" -type d -exec chmod 755 {} \;
chmod +x "$DEB_DIR/usr/bin/fast-youtrack"
chmod +x "$DEB_DIR/usr/share/fast-youtrack/fast-youtrack"
chmod +x "$DEB_DIR/usr/share/fast-youtrack/fast-youtrack-app"
chmod +x "$DEB_DIR/usr/share/fast-youtrack/subdomain_picker"
chmod +x "$DEB_DIR/DEBIAN/postinst"
chmod +x "$DEB_DIR/DEBIAN/prerm"

# Build the package
echo -e "${YELLOW}Building .deb package...${NC}"
dpkg-deb --build "$DEB_DIR" "$DIST_DIR/fast-youtrack_${VERSION}_amd64.deb"

# Clean up
rm -rf "$DEB_DIR"

echo -e "${GREEN}Package created: fast-youtrack_${VERSION}_amd64.deb${NC}"
echo ""
echo -e "${BLUE}To install:${NC}"
echo -e "  sudo dpkg -i fast-youtrack_${VERSION}_amd64.deb"
echo -e "  sudo apt-get install -f  # Fix any dependency issues"
echo ""
echo -e "${BLUE}To uninstall:${NC}"
echo -e "  sudo apt-get remove fast-youtrack"