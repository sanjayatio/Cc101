echo "removing trailing spaces"
find . -type f -name '*.css'  -exec sed -i 's/[[:space:]]\+$//' {} +
find . -type f -name '*.html' -exec sed -i 's/[[:space:]]\+$//' {} +
find . -type f -name '*.js'   -exec sed -i 's/[[:space:]]\+$//' {} +
echo "trailing spaces removed"
