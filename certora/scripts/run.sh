echo "Apply src patch"
git apply certora/patches/src.patch
echo "Apply solady patch"
git apply certora/patches/solady.patch

certoraRun certora/confs/Atlas_transient.conf $@

echo "Revert src patch"
git apply -R certora/patches/src.patch
echo "Revert solady patch"
git apply -R certora/patches/solady.patch