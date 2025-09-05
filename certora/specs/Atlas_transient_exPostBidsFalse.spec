import "./Atlas_transient.spec";

methods {
    //false would lead down the bidKnownIteration path which is simpler 
   function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
}

use invariant atlasEthBalance;
use invariant atlasEthBalanceEnough;
use rule atlasEthBalanceAlmostEnough;
use rule atlasLockEnvNotChanged;
use invariant atlasLockEnvNotSelf;
use invariant atlasNormallyUnlocked;
use rule atlasTemporaryFundsPreserved;
use invariant atlasUnlockInPhase0;
