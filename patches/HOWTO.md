
# Apply a patch from a sub branch

Since no branch will probably be merged into master,
if necessary you may create and apply a patch.

I found the example on [stackoverflow](http://stackoverflow.com/a/8131164).

From the master branch:

```bash
# Create the patch
git diff branch:full/path/to/foo.txt master:full/path/to/foo-another.txt > mypatch

# Use it
patch < mypatch

# Commit
git commit -m "Applied patch"
```
