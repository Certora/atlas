echo "Apply src patch"
git apply certora/patches/src.patch
echo "Apply solady patch"
git apply certora/patches/solady.patch

certoraRun certora/confs/Atlas_transient.conf --verify AtlasHarness:certora/specs/Atlas_transient_exPostBidsFalse.spec --msg "Atlas exPostBids false - execute" --method "execute((address,uint32,address,uint32,uint32),(address,address,uint256,uint256,uint256,uint256,uint256,address,address,uint32,uint32,address,bytes,bytes),(address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes)[],bytes32,address,address,bool)" $@

certoraRun certora/confs/Atlas_transient.conf --verify AtlasHarness:certora/specs/Atlas_transient_exPostBidsFalse.spec --msg "Atlas exPostBids false - not execute" --exclude_method "execute((address,uint32,address,uint32,uint32),(address,address,uint256,uint256,uint256,uint256,uint256,address,address,uint32,uint32,address,bytes,bytes),(address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes)[],bytes32,address,address,bool)" $@

certoraRun certora/confs/Atlas_transient.conf --verify AtlasHarness:certora/specs/Atlas_transient_exPostBidsTrue.spec --msg "Atlas exPostBids true - execute" --method "execute((address,uint32,address,uint32,uint32),(address,address,uint256,uint256,uint256,uint256,uint256,address,address,uint32,uint32,address,bytes,bytes),(address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes)[],bytes32,address,address,bool)" $@

certoraRun certora/confs/Atlas_transient.conf --verify AtlasHarness:certora/specs/Atlas_transient_exPostBidsTrue.spec --msg "Atlas exPostBids true - not execute" --exclude_method "execute((address,uint32,address,uint32,uint32),(address,address,uint256,uint256,uint256,uint256,uint256,address,address,uint32,uint32,address,bytes,bytes),(address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes)[],bytes32,address,address,bool)" $@

echo "Revert src patch"
git apply -R certora/patches/src.patch
echo "Revert solady patch"
git apply -R certora/patches/solady.patch
