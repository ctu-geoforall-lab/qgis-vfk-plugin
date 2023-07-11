#!/usr/bin/env bash
# build docs
git checkout gh-pages
rm -rf *
touch .nojekyll
git checkout release-3_0 help
cd help
make clean
make html
cd ..
mv help/build/html/* ./
rm -rf help
git add -A
git commit -m "publishing updated docs..."
git push origin gh-pages
# switch back
git checkout release-3_0
