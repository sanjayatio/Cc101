echo list of unmanaged resources
git ls-files --others --exclude-standard
echo cached list
git diff --numstat --cached
echo temporary list
git diff --numstat
echo fin
