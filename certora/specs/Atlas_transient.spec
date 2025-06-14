import "./ERC20/erc20cvl.spec";
// import "./MathSummaries.spec";
//using AtlasVerification as AtlasVerification;
using FastLaneOnlineControl as FastLaneOnlineControl;

methods{ 
    //envfree getters
    function AtlasHarness.getLockPhase() external returns uint8 envfree;
    function AtlasHarness.getBorrowLedgerBorrows() external returns uint128 envfree;
    function AtlasHarness.getBorrowLedgerRepays() external returns uint128 envfree;

    // view functions - same approximations 
    //function _.CALL_CONFIG() external => DISPATCHER(true);
    function _.getDAppConfig(Atlas.UserOperation) external => NONDET;
    // function _.initialGasUsed(uint256) external => NONDET;
    function _._computeSalt(address, address, uint32) internal => NONDET;
    //function AtlasVerification.verifySolverOp(Atlas.SolverOperation, bytes32 ,uint256, address, bool) external returns uint256 => NONDET;
    function Escrow._checkSolverBidToken(address, address, uint256) internal returns uint256 => NONDET;
    function Escrow._validateSolverOpDeadline(Atlas.SolverOperation calldata, Atlas.DAppConfig memory) internal returns uint256 => NONDET;
    function AtlasHarness.solverCall(Atlas.Context ctx, Atlas.SolverOperation solverOp, uint256 bidAmount, bytes returnData) external returns (Atlas.SolverTracker) with (env e) =>
        solverCallSummary(e);

    function _.validateCalls(Atlas.DAppConfig, Atlas.UserOperation,
        Atlas.SolverOperation[] solverOps,
        Atlas.DAppOperation dAppOp,
        uint256 metacallGasLeft,
        uint256 msgValue,
        address msgSender,
        bool isSimulation) external with (env e) => havocAllPreserveLockEnv(e) expect (Atlas.Context);
    function _.preOpsWrapper(Atlas.UserOperation) external with (env e) => havocAllPreserveLockEnv(e) expect (Atlas.Context);
    function _.userWrapper(Atlas.UserOperation) external with (env e) => havocAllPreserveLockEnv(e) expect (Atlas.Context);
    function _.getDAppSignatory() external with (env e) => havocAllPreserveLockEnv(e) expect (Atlas.Context);
    function _.getL1FeeUpperBound() external with (env e) => havocAllPreserveLockEnv(e) expect (Atlas.Context);
    function _.CALL_CONFIG() external with (env e) => havocAllPreserveLockEnv(e) expect (Atlas.Context);
    function Base._control() internal returns (address)=> FastLaneOnlineControl;
    function _.isUnlocked() external => DISPATCHER(true);

    
    // getters
    function getLockEnv() external returns address envfree;
    function getLockCallConfig() external returns uint32 envfree;
    function getLockPhase() external returns uint8 envfree;
    function getActiveEnvironment() external returns address envfree;

    // ND need to check these:
    //false would lead down the bidKnownIteration path which is simpler 
//    function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
    // 
//    function Escrow._checkTrustedOpHash(Atlas.DAppConfig memory, bool, Atlas.UserOperation calldata, Atlas.SolverOperation calldata, uint256) internal returns uint256 => NONDET;


    function GasAccounting._updateAnalytics(Atlas.EscrowAccountAccessData memory, bool, uint256) internal => NONDET;

    function Factory._getOrCreateExecutionEnvironment(address, address, uint32) internal returns address => getOrCreateExecutionEnvironmentSummary();

    function FactoryLib._getMimicCreationCode(address, address, uint32) internal returns bytes memory => getMimicCodeSummary();

    // need to fix:
    //function _.solverPostTryCatch(Atlas.SolverOperation,bytes,Atlas.SolverTracker) external => NONDET;
    //function _.solverPreTryCatch(uint256,Atlas.SolverOperation,bytes) external => NONDET;
    //function _.atlasSolverCall(address,address,address,uint256,bytes,bytes) external => NONDET;

    // unresolved external in _._(address, uint256, bytes) => DISPATCH [
    //     FastLaneOnlineControl.allocateValueCall(bool, address, uint256, bytes)
    // ] default HAVOC_ALL;

    // unresolved external in _.solverPreTryCatch(uint256, Atlas.SolverOperation, bytes) => DISPATCH [
    //     FastLaneOnlineControl.preSolverCall(Atlas.SolverOperation,bytes)
    // ] default HAVOC_ALL;

    // unresolved external in _.preOpsWrapper(Atlas.UserOperation) => DISPATCH [
    //     FastLaneOnlineControl.preOpsCall(Atlas.UserOperation)
    // ] default HAVOC_ALL;
    
    //unresolved external in _.postOpsWrapper(bool, bytes) => DISPATCH [
    //    FastLaneOnlineControl.postOpsCall(bool, bytes)
    //] default HAVOC_ALL;
    
    //unresolved external in _.userWrapper(Atlas.UserOperation) => DISPATCH [
    //    FastLaneOnlineControl.postOpsCall(bool, bytes)
    //] default HAVOC_ALL;

    function _.allocateValue(bool, address, uint256, bytes) external with (env e) => havocAllPreserveLockEnv(e) expect (Atlas.Context);


    unresolved external in _._ => DISPATCH [
        _.allocateValue(bool, address, uint256, bytes)
    ] default HAVOC_ALL;


    //unresolved external in _._ => DISPATCH [ ] default havocAllPreserveLockEnv(e) 
    function _.solverPreTryCatch(
        uint256 bidAmount,
        Atlas.SolverOperation solverOp,
        bytes returnData
    ) external => DISPATCHER(true);

    function _.atlasSolverCall(
        address solverOpFrom,
        address executionEnvironment,
        address bidToken,
        uint256 bidAmount,
        bytes solverOpData,
        bytes extraReturnData
    )
        external with (env e) => atlasSolverCallSummary(e) expect void;

    function _.solverPostTryCatch(
        Atlas.SolverOperation  solverOp,
        bytes  returnData,
        Atlas.SolverTracker  solverTracker
    )
        external => DISPATCHER(true);

    function AtlasHarness.execute(Atlas.DAppConfig dConfig, Atlas.UserOperation userOp, Atlas.SolverOperation[] solverOps, bytes32 userOpHash, address executionEnvironment, address bundler, bool isSimulation) external
        returns (Atlas.Context memory) with (env e) => executeSummary(e);
        
    function AtlasHarness.havocAll() external => HAVOC_ALL;

    // limiting to without delegate call
    function CallBits.needsPostSolverCall(uint32 callConfig) internal returns (bool) => ALWAYS(false) ;

    //function CallBits.needsPostOpsCall(uint32 callConfig) internal returns (bool)  => ALWAYS(false) ;

    //function FastLaneOnlineControl.preOpsCall(Atlas.UserOperation) external returns (bytes) => HAVOC_ALL;
    //function FastLaneOnlineControl.allocateValueCall(bool, address, uint256, bytes) external => HAVOC_ALL;

}

function getMimicCodeSummary() returns bytes {
    bytes result;
    return result;
}

function getOrCreateExecutionEnvironmentSummary() returns address {
    address result;
    require(result != 0 && result != currentContract, "getOrCreate returns valid address");
    return result;
}

/*----------------------------------------------------------------------------------------------------------------
                                                 GHOSTS & HOOKS 
----------------------------------------------------------------------------------------------------------------*/

ghost mapping(uint256 => uint256) calldataCostGhost;
ghost mapping(uint256 => uint256) initialGasUsed;

// ghost tracking the bonded, unbonded and unbonding balances
ghost mapping(address => uint112) bondedBalances {
    init_state axiom (usum address a. bondedBalances[a]) == 0;
}
ghost mapping(address => uint112) unbondedBalances {
    init_state axiom (usum address a. unbondedBalances[a]) == 0;
}
ghost mapping(address => uint112) unbondingBalances {
    init_state axiom (usum address a. unbondingBalances[a]) == 0;
}


definition sumOfBonded() returns mathint =
    (usum address a. bondedBalances[a]) - bondedBalances[currentContract];
definition sumOfUnbonded() returns mathint =
    (usum address a. unbondedBalances[a]) - unbondedBalances[currentContract];
definition sumOfUnbonding() returns mathint =
    (usum address a. unbondingBalances[a]) - unbondingBalances[currentContract];



// Hooks for bonded balances
hook Sstore S_accessData[KEY address a].bonded uint112 new_value (uint112 old_value) {
    bondedBalances[a] = new_value;
}
hook Sload uint112 value S_accessData[KEY address a].bonded {
     require(value == bondedBalances[a], "mirror storage in ghost");
}

// SSTORE hook for unbonded balances
hook Sstore s_balanceOf[KEY address a].balance uint112 new_value (uint112 old_value) {
    unbondedBalances[a] = new_value;
}

hook Sload uint112 value s_balanceOf[KEY address a].balance {
     require(value == unbondedBalances[a], "mirror storage in ghost");
}

// SSTORE hook for unbonding balances
hook Sstore s_balanceOf[KEY address a].unbonding uint112 new_value (uint112 old_value) {
    unbondingBalances[a] = new_value;
}

hook Sload uint112 value s_balanceOf[KEY address a].unbonding {
     require(value == unbondingBalances[a], "mirror storage in ghost");
}

/*----------------------------------------------------------------------------------------------------------------
                                                 CVL FUNCTIONS
----------------------------------------------------------------------------------------------------------------*/

/* ghost variable that remembers if we are inside a solverCall and have not forwarded the value yet */
ghost mathint solverCallValue {
    init_state axiom solverCallValue == 0;
}

function dispatchDefault(){

}



/* summary function for execute and other functions, this is proved by the rule atlasExecuteDoesntChangeLockEnv */
function genericSummary(env e, mathint expectedChangeSolverCallValue) {
    address lockEnvBefore = getLockEnv();
    mathint oldSolverCallValue = solverCallValue;
    havocAll(e);
    require lockEnvBefore == getLockEnv();
    require solverCallValue == oldSolverCallValue + expectedChangeSolverCallValue;
}

function havocAllPreserveLockEnv(env e) returns Atlas.Context {
    Atlas.Context ctx;
    genericSummary(e, 0);
    return ctx;
}

/* summary function for solverCall; this adds the value to the solverCallValue temporary funds */
function solverCallSummary(env e) returns Atlas.SolverTracker {
    Atlas.SolverTracker tracker;
    solverCallValue = solverCallValue + e.msg.value;
    assert getLockEnv() != 0; // precondition for solverCall

    genericSummary(e, -e.msg.value);
    return tracker;
}

/* summary function for execute; this checks that it is only called in locked state. */
function executeSummary(env e) returns Atlas.Context {
    Atlas.Context ctx;

    assert getLockEnv() != 0; // precondition for execute
    genericSummary(e, 0);

    return ctx;
}


/* summary function for solverCall; this checks the precondition required by its invariant for self-calls */
function atlasSolverCallSummary(env e) {
    solverCallValue = solverCallValue - e.msg.value;

    genericSummary(e, 0);
}


/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/

weak invariant atlasNormallyUnlocked() 
    getLockEnv() == 0;


strong invariant atlasLockEnvNotSelf() 
    getLockEnv() != currentContract;

strong invariant atlasUnlockInPhase0()
    getLockEnv() == 0 => getLockPhase() == 0
    {
        preserved solverCall(Atlas.Context ctx, Atlas.SolverOperation solverOp, uint256 bidAmount, bytes returnData) with (env e) {
            require e.msg.sender == currentContract => getLockEnv() != 0;
        }
        preserved execute(Atlas.DAppConfig config, Atlas.UserOperation userOp, Atlas.SolverOperation[] solverOps, bytes32 userOpHash, address executionEnvironment, address bundler, bool isSimulation) with (env e) {
            require e.msg.sender == currentContract => getLockEnv() != 0;
        }
    }

strong invariant atlasEthBalance()
    nativeBalances[currentContract] == sumOfBonded() + sumOfUnbonded() + sumOfUnbonding() + currentContract.S_cumulativeSurcharge + (getLockEnv() == 0 ? 0 : getBorrowLedgerRepays() - getBorrowLedgerBorrows()) + solverCallValue
    {
        preserved onTransactionBoundary {
            requireInvariant atlasNormallyUnlocked();
        }

        preserved with (env e){
            require(e.msg.sender != 0, "zero address cannot call");
            requireInvariant atlasLockEnvNotSelf();
            requireInvariant atlasUnlockInPhase0();
        }

        preserved execute(Atlas.DAppConfig config, Atlas.UserOperation userOp, Atlas.SolverOperation[] solverOps, bytes32 userOpHash, address executionEnvironment, address bundler, bool isSimulation) with (env e) {
            require e.msg.sender == currentContract => getLockEnv() != 0;
            require(e.msg.sender != 0, "zero address cannot call");
            requireInvariant atlasLockEnvNotSelf();
            requireInvariant atlasUnlockInPhase0();
        }

        preserved reconcile(uint256 v) with (env e){
            // reconcile is never called by Atlas itself
            require(e.msg.sender != currentContract, "no self call");
            // also require the things above.
            require(e.msg.sender != 0, "zero address cannot call");
            requireInvariant atlasLockEnvNotSelf();
            requireInvariant atlasUnlockInPhase0();
        }

        preserved withdrawSurcharge() with (env e){
            // withdrawSurcharge is never called by Atlas itself.
            // this would violate the invariant as the surcharge is burned.
            require(e.msg.sender != currentContract, "no self call");
            // also require the things above.
            require(e.msg.sender != 0, "zero address cannot call");
            requireInvariant atlasLockEnvNotSelf();
            requireInvariant atlasUnlockInPhase0();
        }
    }


rule atlasLockEnvNotChanged(method f, calldataarg args) {
    env e;
    if (f.selector == sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], bytes32, address, address, bool).selector) {
        // execute is only called by Atlas itself in the locked state.
        require e.msg.sender == currentContract => getLockEnv() != 0;
    }

    address lockEnvBefore = getLockEnv();
    f(e, args);
    address lockEnvAfter = getLockEnv();
    assert lockEnvBefore == lockEnvAfter;
}

rule atlasSolverCallValuePreserved(method f, calldataarg args) {
    env e;
    mathint solverCallValueBefore = solverCallValue;
    if (f.selector == sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], bytes32, address, address, bool).selector) {
        // execute is only called by Atlas itself in the locked state.
        require e.msg.sender == currentContract => getLockEnv() != 0;
    }

    f(e, args);
    mathint solverCallValueAfter = solverCallValue;
    mathint expectedChange = 0;
    if (f.selector == sig:solverCall(Atlas.Context, Atlas.SolverOperation, uint256, bytes).selector) {
        expectedChange = - e.msg.value;
    }
    assert solverCallValueAfter == solverCallValueBefore + expectedChange;
}
