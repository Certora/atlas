import "./ERC20/erc20cvl.spec";
// import "./MathSummaries.spec";
using AtlasVerification as AtlasVerification;

methods{ 
    function _.CALL_CONFIG() external => DISPATCHER(true);

    function _.getDAppConfig(Atlas.UserOperation) external => NONDET;
    function _.initialGasUsed(uint256) external => NONDET;
    function _._computeSalt(address, address, uint32) internal => NONDET;
    //false would lead down the bidKnownIteration path which is simpler 
    function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
    function AtlasVerification.verifySolverOp(Atlas.SolverOperation, bytes32 ,uint256, address, bool) external returns uint256 => NONDET;
    function Escrow._checkSolverBidToken(address, address, uint256) internal returns uint256 => NONDET;
    function Escrow._validateSolverOpDeadline(Atlas.SolverOperation calldata, Atlas.DAppConfig memory) internal returns uint256 => NONDET;
    function Escrow._checkTrustedOpHash(Atlas.DAppConfig memory, bool, Atlas.UserOperation calldata, Atlas.SolverOperation calldata, uint256) internal returns uint256 => NONDET;
    function GasAccounting._updateAnalytics(Atlas.EscrowAccountAccessData memory, bool, uint256) internal => NONDET;
    function Factory._getOrCreateExecutionEnvironment(address, address, uint32) internal returns address => NONDET;
    function _.getCalldataCost(uint256) external => CONSTANT;
    function GasAccounting._settle(Atlas.Context memory, uint256, address) internal returns (uint256, uint256) => settleCVL();
    function Escrow.errorSwitch(bytes4) internal returns (uint256) => NONDET;

    // getters
    function getLockEnv() external returns address envfree;
    function getLockCallConfig() external returns uint32 envfree;
    function getLockPhase() external returns uint8 envfree;


    // function AtlasVerification.validateCalls(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation,uint256, address, bool) external returns Atlas.ValidCallsResult => NONDET;
    // function _._executeUserOperation(Atlas.Context memory, Atlas.DAppConfig memory, Atlas.UserOperation calldata, bytes memory) internal  => NONDET;
    // function Escrow._executeUserOperation(Atlas.Context memory, Atlas.DAppConfig memory, Atlas.UserOperation calldata, bytes memory) internal returns bytes memory => _executeUserOperationCVL;
    // checking if this avoids the failed to locate function error
    // function _._allocateValueCall(address, uint256, bytes calldata) internal => NONDET;
    // function _._getCallConfig(uint32) internal => NONDET;

    // function _._getMimicCreationCode(address, address, uint32) internal => CONSTANT;
    
    // unresolved external in _._ => DISPATCH [
    //     // ExecutionEnvironment.preOpsWrapper(Atlas.UserOperation)
    //     ExecutionEnvironment.postOpsWrapper(bool, bytes),
        

    // ] default HAVOC_ALL;
    // function _executePostOpsCall(Atlas.Context memory ctx, bool solved, bytes returnData memory) internal => _executePostOpsCallCVL(ctx, solved, returnData);
    // _.getCalldataCost() external => DISPATCHER(true);
    
    // unresolved external in _._ => DISPATCH [
    //     // FactoryLib.getOrCreateExecutionEnvironment(address, address, uint32, bytes32),
    //     // AtlasVerification.validateCalls(Atlas.DAppConfig, Atlas.UserOperation, 
    //                                     // Atlas.SolverOperation[], Atlas.DAppOperation, uint256, address, bool),
    //     // Atlas.execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool),
    //     // ExecutionEnvironment.solverPreTryCatch(uint256, Atlas.SolverOperation, bytes),
    //     // SolverBase.atlasSolverCall(address, address, address, uint256, bytes, bytes),
    //     FastLaneOnlineControl.postOpsCall(bool, bytes)
    // ] default HAVOC_ALL;
}
/*----------------------------------------------------------------------------------------------------------------
                                                 GHOSTS & HOOKS 
----------------------------------------------------------------------------------------------------------------*/


// ghost tracking the sum of atlETH bonded balances
persistent ghost mathint sumOfBonded{
    init_state axiom sumOfBonded == 0;
}
// ghost tracking the sum of atlETH unbonded balances
persistent ghost mathint sumOfUnbonded{
    init_state axiom sumOfUnbonded == 0;
}
// ghost tracking the sum of atlETH unbonding balances
persistent ghost mathint sumOfUnbonding{
    init_state axiom sumOfUnbonding == 0;
}

ghost bool transientInvariantHolds{
    init_state axiom transientInvariantHolds == false;
}
// ghost bytes[8] _executeUserOperationCVL;

// ghost tracking the transient variable t_withdrawals
persistent ghost uint256 withdrawals{
    init_state axiom withdrawals == 0;
}
// ghost tracking the transient variable t_deposits
persistent ghost uint256 deposits{
    init_state axiom deposits == 0;
}


// Hooks for bonded balances
hook Sstore S_accessData[KEY address a].bonded uint112 new_value (uint112 old_value) {
    sumOfBonded = sumOfBonded - old_value + new_value;
}
hook Sload uint112 value S_accessData[KEY address a].bonded {
     require value <= sumOfBonded;
}


// SSTORE hook for unbonded balances
hook Sstore s_balanceOf[KEY address a].balance uint112 new_value (uint112 old_value) {
    sumOfUnbonded = sumOfUnbonded - old_value + new_value;
}

hook Sload uint112 value s_balanceOf[KEY address a].balance {
     require value <= sumOfUnbonded;
}


// SSTORE hook for unbonding balances
hook Sstore s_balanceOf[KEY address a].unbonding uint112 new_value (uint112 old_value) {
    sumOfUnbonding = sumOfUnbonding - old_value + new_value;
}

hook Sload uint112 value s_balanceOf[KEY address a].unbonding {
     require value <= sumOfUnbonding;
}

// update ghost withdrawals and deposits
hook ALL_TSTORE(uint256 loc, uint256 v) {
    if (loc == 7) 
        withdrawals = v;
    if (loc == 8) 
        deposits = v; 
}

hook ALL_TLOAD(uint loc) uint v {
    if (loc == 7) 
        withdrawals = v; 
    if (loc == 8) 
        deposits = v; 
}


/*----------------------------------------------------------------------------------------------------------------
                                                 CVL FUNCTIONS
----------------------------------------------------------------------------------------------------------------*/


function settleCVL() returns (uint256, uint256){
    transientInvariantHolds = nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    uint256 claimPaid;
    uint256 gasSurcharge;
    return (claimPaid, gasSurcharge);
}

/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/

// during metacall execution, before _settle(),  Atlas ETH balance = sum of AtlETH accounts {unbonded + bonded + unbonding} + cumulativeSurcharge + deposits - withdrawals
// https://prover.certora.com/output/11775/c56863334d364e5b9bd6d0172d51728f?anonymousKey=c9a7484725a84b303d12579dbd2ed3adf987b8bb - with validateCall NONDET summary
// https://prover.certora.com/output/11775/51159d431b5441df964db48da791d95d?anonymousKey=9728790aecd80e499942b1897fa504d51512ec69 - latest run
// https://prover.certora.com/output/11775/ebd59e95a71e4217a5d0df7b2c8e7957?anonymousKey=6604df6a0635f905673136e7852379d4f8d029fe - without _bidKnownIteration and _bidFindingIteration NONDET
// https://prover.certora.com/output/11775/2c95bb7652b741888c73929ca14d33ee?anonymousKey=e3f40fc7e27e39578172b925939fa6233043442f - with verifySolverOp and _checkSolverBidToken NONDET
// https://prover.certora.com/output/11775/aca79dec01ba44eb980ed9628cdc1195?anonymousKey=31b35cf3427000659762cff4d05b229ecf5647b8 - with further simplification across the metacall function 
// https://prover.certora.com/output/11775/9210014c28cb4143935d829b005e018b?anonymousKey=4e2757e025e534fdfdb846e4d1188925ae468ac8 - with solverOps length > 0 and all the above simplification
// https://prover.certora.com/output/11775/ad4f643320a54f099f386044f8b016c4?anonymousKey=70b3a9721b0650ae6a0b095d8d71047781f6878b - with John's patch
// https://prover.certora.com/output/11775/1a05e4e8a04c42d9aefc6e17bbb7f873?anonymousKey=358464c9808d58df823706b15cecb6002c7c0765 - wtih bid known path and basic sanity
// https://prover.certora.com/output/11775/930ef8e8686242668f7eef3a2253c377?anonymousKey=b421b8c9843045960f7c27f3b88a209beadf24f5 - with bid known path and no sanity
// https://prover.certora.com/output/11775/2d9761540dcf462dbab6c7085207aa5e?anonymousKey=8dfbc71e171affd9365b67b1e954d5139ba5e299 - with bid finding path and no sanity
// https://prover.certora.com/output/11775/a12df0b4d607425780975ea845d7151d?anonymousKey=d8c7c5a4b2577f94b4ed19938c4547b67a7f9d80 - with bid finding path and basic sanity
// https://prover.certora.com/output/11775/e25d3ab6c2504c71b5811576f0ebeee0?anonymousKey=86b7a752a643dcaa1d498c1eacacf27be2ea454a - rerun with John's latest branch bid finding
// https://prover.certora.com/output/11775/ccf076104d214ff5837b0bc9e6052209?anonymousKey=bd7b69177f106598e488783d2133f54056e6c259 - with john's latest branch and bid known
// https://prover.certora.com/output/11775/402aef9c2d0d4e3abcaa50d08ff15589?anonymousKey=edcf7a68b7e60ef11010f24f053556c339bcbd0a - with bid known and withdrawls deposits 0 in preserved block
strong invariant atlasEthBalanceGeSumAccountsSurchargeTransientMetacall()
    nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals
    filtered {f -> f.selector == sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector}
        {
            preserved metacall(Atlas.UserOperation userOp, Atlas.SolverOperation[] solverOps, Atlas.DAppOperation dAppOp, address gasRefundBeneficiary) with (env e) {
                require solverOps.length > 0;
                // ghosts tracking transient variables, safe to assume them as 0 before induction step
                require withdrawals == 0;
                require deposits == 0;
                }
        }

// https://prover.certora.com/output/11775/aeb505982adf4f398e78c54c9c7ed4f8?anonymousKey=854d8913789f81276bf637f94e739bfa9c936d25 - first run
// https://prover.certora.com/output/11775/6ff5661fd8af42a0981b578236cfa276?anonymousKey=1e76fad71e16b6edc5b58448fc9f64c34979ffcb - with msg.sender != currentContract
// https://prover.certora.com/output/11775/d82703f855e449038420a3731bbb197a?anonymousKey=616cd5ca6df4bb194a23716307a95ecd0403bc96 - with persistent ghost - killed out of memory
// https://prover.certora.com/output/11775/44589c1c8e52401ab8be2c0ebd935221?anonymousKey=dbe05a170fffe33b82fec282ab368e0d93dcba4f - with depth 0 - OOM
// https://prover.certora.com/output/11775/708bc6fa8bb94a1abfa44cc53f59edd4?anonymousKey=1ff9a64dd1e3c3a47fc421502f82f332fb2fa289 - with z3 10 seeds
// https://prover.certora.com/output/11775/49d5044c6a8345ba858a5de5ad6e595d?anonymousKey=13b8e3c21cdf50d41c5dba2788770286fe0f4fc7 - with z3 1 seed
// https://prover.certora.com/output/11775/aab443a14d344cbca27ee67c3f89b0c7?anonymousKey=d51e0be74946568a8a8b7e9af7dfbdb8fc60c453 - without WETH and solver in the scene
// https://prover.certora.com/output/11775/6b2f46b8b841462e9de78e6b873582d5?anonymousKey=2fec13b3b66b1202047f011a8834380c4978b8b1 - without solver restriction
// https://prover.certora.com/output/11775/56fb5af39aa443ccbe930c0af0bf3205?anonymousKey=58d29a095c82c46306fbdd7c19564ab44acca753 - with calldata args
// Jaroslav's OOM solution conf and munging
// https://prover.certora.com/output/11775/9b743d8040994f2f9b2132ddb9a34e2f?anonymousKey=a50a0cf58b6b14bcf9478bbc7564f09a2010e2a3 - with AlteredControl.selector - HARDSTOP
// https://prover.certora.com/output/11775/17fc60eedadb426f9f2601b9705567cc?anonymousKey=fa667fdd056b5c30d6abf65f1e37bae8dbfc3cbf - with InsufficientEscrow - HARDSTOP
// https://prover.certora.com/output/11775/e046df149c2745188724f8af3eb937d8?anonymousKey=98cf002f251c4f814be485cf5a1c88b9ecda5555 - wtih PreSolverFailed - HARDSTOP
// https://prover.certora.com/output/11775/ed84d91d20b547cca0fa7acfef6c85ee?anonymousKey=008b58ebc1a91d30924ddc4698ebf9fe5533b605 - wtih SolverOpReverted - HARDSTOP
// https://prover.certora.com/output/11775/f4360d7335e140f8a02142c727b30f9a?anonymousKey=75afea30f7e8850ca9f0132d1fff428d7a917a9c - wtih PostSolverFailed - HARDSTOP
// https://prover.certora.com/output/11775/407982dafae84764a1300a1de3d95fbc?anonymousKey=90e0e71b0180c61874187d6da00c67f292fe7777 - wtih BidNotPaid - HARDSTOP
// https://prover.certora.com/output/11775/efac8bfe70e64688a29e9d345214f43f?anonymousKey=21a2e86b96d6733087b815a5d189511eb6df6d86 - wtih InvalidSolver - HARDSTOP
// https://prover.certora.com/output/11775/f90fc40d64a64f068452b4996267d8bf?anonymousKey=b910ac13c40b6f7f6260edf5698d7a37f91d5b3e - wtih BalanceNotReconciled - HARDSTOP
// https://prover.certora.com/output/11775/05620195c03641a2bc51bc9ec3e7d5ba?anonymousKey=a880be88b76b13a76490be55865b55d50baeeac6 - wtih CallbackNotCalled - HARDSTOP
// https://prover.certora.com/output/11775/22c120f0968e4dc2830957a8b3490e09?anonymousKey=7d3eb4f498bd7cc8b50284b7f4fd9c7c80ec62ea - wtih InvalidEntry - HARDSTOP
// https://prover.certora.com/output/11775/5fb4392b51894070a7b241a6624b0e5f?anonymousKey=91d41eb499ee8b0f2754913e9dc633ae02784e39 - with else case - HARDSTOP
// without sanity
// https://prover.certora.com/output/11775/b8276b70ca6a417f86538cebb27ca002?anonymousKey=bf2e9f1c59103b4e353a0914a0500e21d22268cf - with AlteredControl.selector - PASSING
// https://prover.certora.com/output/11775/350b7930ab2344bebc535218ce1edd86?anonymousKey=31debb4730eaeddfc4eb89db839b492d07bed95e - with InsufficientEscrow.selector - PASSING
// https://prover.certora.com/output/11775/14f2ae35711b4bbc97306ab5e9a262d0?anonymousKey=c51aadbb447cffb5ddd56b82c47e5cc79e0e4779 - with PreSolverFailed.selector - PASSING
// https://prover.certora.com/output/11775/ec00f74d2e264a4da7728142b08ece8a?anonymousKey=862ba406991e8082853c9f324382d2fcacc99ffd - with SolverOpReverted.selector - PASSING
// https://prover.certora.com/output/11775/747a661b5cdf499bb186fb08a7d07b3f?anonymousKey=b1657cd4c41eb4ce698c14e58464882e9c2a54c8 - with PostSolverFailed.selector - PASSING
// https://prover.certora.com/output/11775/6be05f5aa9fa4d5ca6a13c489d3e3c9b?anonymousKey=12670f29efb3cd8396c7b646f897f5df627828c4 - with BidNotPaid.selector - PASSING
// https://prover.certora.com/output/11775/071dcbea89fb4779be82fb7c436dfeb9?anonymousKey=f11291f9058ed0157a72668263d810a60dc340f0 - with InvalidSolver.selector - PASSING
// https://prover.certora.com/output/11775/70bb055fa93c48fb97694dfd0cdb0268?anonymousKey=b821c4f51d7ecb373ef612e04233e64938927c4d - with BalanceNotReconciled.selector - PASSING
// https://prover.certora.com/output/11775/74f80b214f85459dbee9b6f1e2dc12c2?anonymousKey=14a88ff6f300c8d0badb9e1fc9d1f4949655d083 - with CallbackNotCalled.selector - PASSING
// https://prover.certora.com/output/11775/ab27a95cd8084fbbbfad28933d4e3eb7?anonymousKey=ec8a8ec17ddf6c055c01bd82b7636fe8fc1b8afa - with InvalidEntry.selector - PASSING
// https://prover.certora.com/output/11775/c23947dde37549788d4ee9190a1a6d60?anonymousKey=582661b8e66fe1d4986f6b0189295317d6de4598 - with else case - PASSING
// with munging to NONDET errorSwitch in escrow
// https://prover.certora.com/output/11775/3ed5f875d28e44b1b4713b8f34b80b6f?anonymousKey=a036b958281b555bdf8cbe8c67f265f8bd61348b - wtih errorSwitch NONDET - PASSING

rule atlasEthBalanceGeSumAccountsSurchargeTransientMetacallRule(){
    require withdrawals == 0; 
    require deposits == 0; 
    
    env e;
    require e.msg.sender != currentContract;
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    // Atlas.UserOperation userOp;
    // Atlas.SolverOperation[] solverOps;
    // Atlas.DAppOperation DAppOp;
    // address refBeneficiary;

    calldataarg args;

    metacall(e, args);

    assert transientInvariantHolds;
}