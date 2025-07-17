import "./Atlas_transient.spec";

methods {
    //false would lead down the bidKnownIteration path which is simpler.
    // here we take the harder path.
   function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(true);
}

use invariant atlasEthBalance;
use rule atlasLockEnvNotChanged;
use invariant atlasLockEnvNotSelf;
use invariant atlasNormallyUnlocked;
use rule atlasSolverCallValuePreserved;
use invariant atlasUnlockInPhase0;