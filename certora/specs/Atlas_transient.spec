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
    function _.getCalldataCost(uint256 l) external => calldataCostGhost[l] expect (uint256) ALL;
    function _._getCalldataCost(uint256 l) internal => calldataCostGhost[l] expect (uint256); // why ext summary wasn't applied? because we needed all. but the wrapper also isn't needed

    function _.initialGasUsed(uint256 l) external => initialGasUsed[l] expect (uint256) ALL;
    function Escrow.errorSwitch(bytes4) internal returns (uint256) => NONDET;
    function EscrowBits.canExecute(uint256) internal returns (bool) => ALWAYS(true);
    // function Escrow._solverOpWrapper(Atlas.Context memory, Atlas.SolverOperation calldata, uint256, uint256, bytes memory) internal returns (uint256, Atlas.SolverTracker memory) => nothingSolverOp();

    function _.preOpsWrapper(Atlas.UserOperation) external => NONDET;
    function _.userWrapper(Atlas.UserOperation) external => NONDET;
    function _.getDAppSignatory() external => NONDET;
    function _.getL1FeeUpperBound() external => NONDET;
    function _.CALL_CONFIG() external => NONDET;
    function Base._control() internal returns (address)=> FastLaneOnlineControl;
    function _.isUnlocked() external => DISPATCHER(true);

    
    // function _.allocateValue(address,uint256,bytes) external => NONDET; // SG xxx may contribute balance to Atlas, use better summary
    function _.postOpsWrapper(bool,bytes) external => NONDET;

    // getters
    function getLockEnv() external returns address envfree;
    function getLockCallConfig() external returns uint32 envfree;
    function getLockPhase() external returns uint8 envfree;
    function getActiveEnvironment() external returns address envfree;

    // ND need to check these:
    //false would lead down the bidKnownIteration path which is simpler 
    function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
    // 
    function Escrow._checkTrustedOpHash(Atlas.DAppConfig memory, bool, Atlas.UserOperation calldata, Atlas.SolverOperation calldata, uint256) internal returns uint256 => NONDET;


    function GasAccounting._updateAnalytics(Atlas.EscrowAccountAccessData memory, bool, uint256) internal => NONDET;

    function Factory._getOrCreateExecutionEnvironment(address, address, uint32) internal returns address => NONDET;

    function FactoryLib._getMimicCreationCode(address, address, uint32) internal returns bytes memory => getMimicCodeSummary();

    // need to fix:
    //function _.solverPostTryCatch(Atlas.SolverOperation,bytes,Atlas.SolverTracker) external => NONDET;
    //function _.solverPreTryCatch(uint256,Atlas.SolverOperation,bytes) external => NONDET;
    //function _.atlasSolverCall(address,address,address,uint256,bytes,bytes) external => NONDET;

    unresolved external in _._(address, uint256, bytes) => DISPATCH [
        FastLaneOnlineControl.allocateValueCall(bool, address, uint256, bytes)
    ] default HAVOC_ALL;

    unresolved external in _.solverPreTryCatch(uint256, Atlas.SolverOperation, bytes) => DISPATCH [
        FastLaneOnlineControl.preSolverCall(Atlas.SolverOperation,bytes)
    ] default HAVOC_ALL;

    unresolved external in _.preOpsWrapper(Atlas.UserOperation) => DISPATCH [
        FastLaneOnlineControl.preOpsCall(Atlas.UserOperation)
    ] default HAVOC_ALL;
    
    //unresolved external in _.postOpsWrapper(bool, bytes) => DISPATCH [
    //    FastLaneOnlineControl.postOpsCall(bool, bytes)
    //] default HAVOC_ALL;
    
    //unresolved external in _.userWrapper(Atlas.UserOperation) => DISPATCH [
    //    FastLaneOnlineControl.postOpsCall(bool, bytes)
    //] default HAVOC_ALL;

    unresolved external in _._allocateValue(Atlas.Context, Atlas.DAppConfig, uint256, bytes) => DISPATCH [
        ExecutionEnvironment.allocateValue(bool, address, uint256, bytes)
    ] default HAVOC_ALL;
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
        external => DISPATCHER(true);

    function _.solverPostTryCatch(
        Atlas.SolverOperation  solverOp,
        bytes  returnData,
        Atlas.SolverTracker  solverTracker
    )
        external => DISPATCHER(true);

    function AtlasHarness.execute(
        Atlas.DAppConfig dConfig,
        Atlas.UserOperation userOp,
        Atlas.SolverOperation[] solverOps,
        bytes32 userOpHash,
        address executionEnvironment,
        address bundler,
        bool isSimulation
    ) external
        returns (Atlas.Context memory) => HAVOC_ALL;

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

/*----------------------------------------------------------------------------------------------------------------
                                                 GHOSTS & HOOKS 
----------------------------------------------------------------------------------------------------------------*/

ghost mapping(uint256 => uint256) calldataCostGhost;
ghost mapping(uint256 => uint256) initialGasUsed;

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

persistent ghost bool called_extcall;

// We are hooking here on "CALL" opcodes in order to capture if there was a storage access before or/and after a call
hook CALL(uint g, address addr, uint value, uint argsOffset, uint argsLength, uint retOffset, uint retLength) uint rc {

    called_extcall = called_extcall || addr != currentContract;
}

/*----------------------------------------------------------------------------------------------------------------
                                                 CVL FUNCTIONS
----------------------------------------------------------------------------------------------------------------*/

function dispatchDefault(){

}
/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/

weak invariant atlasNormallyUnlocked() 
    getLockEnv() == 0;

strong invariant atlasEthBalanceGeSumAccountsSurchargeTransient()
    nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + (getLockEnv() == 0 ? 0 : getBorrowLedgerRepays() - getBorrowLedgerBorrows())
    {
        preserved onTransactionBoundary {
            requireInvariant atlasNormallyUnlocked();
        }

        preserved with (env e){
            require(e.msg.sender != 0, "zero address cannot call");
            require(e.msg.sender != currentContract, "no self call");
        }
    }


rule atlasEthBalanceGeSumAccountsSurchargeTransientMetacallRule(){
    
    env e;
    require e.msg.sender != currentContract;
    
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge;

    calldataarg args;

    metacall(e, args);

    assert transientInvariantHolds;
    satisfy true;
}


rule sanity() {
    env e;
    require !transientInvariantHolds;
    require !called_extcall;
    calldataarg args;

    Atlas.UserOperation userOp;
    Atlas.SolverOperation[] solverOps;
    Atlas.DAppOperation dAppOp;
    address gasRefundBeneficiary;

    require solverOps.length == 1;

    metacall(e, userOp, solverOps, dAppOp, gasRefundBeneficiary);

    //metacall(e,args);
    assert false;
    //satisfy  called_extcall ; 
}

rule all(method f) {
    env e;

    require !called_extcall;
    calldataarg args;
    f(e,args);
    satisfy  called_extcall ; 
}


rule whichFunctionsOnlyThis(method f) filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector} {
    env e;

    calldataarg args;
    f(e,args);
    assert e.msg.sender == currentContract; 
}

rule whichFunctionsOnlyUninitialized(method f) filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector} {
    env e;

    uint8 phase = getLockPhase();
    calldataarg args;
    f(e,args);
    assert phase == 0;
}

rule whichFunctionsOnlyPreOps(method f) filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector} {
    env e;

    uint8 phase = getLockPhase();
    calldataarg args;
    f(e,args);
    assert phase == 1;
}

rule whichFunctionsOnlyUserOperation(method f) filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector} {
    env e;

    uint8 phase = getLockPhase();
    calldataarg args;
    f(e,args);
    assert phase == 2;
}

rule whichFunctionsOnlyPreSolver(method f) filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector} {
    env e;

    uint8 phase = getLockPhase();
    calldataarg args;
    f(e,args);
    assert phase == 3;
}

rule whichFunctionsOnlySolverOperation(method f) filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector} {
    env e;

    uint8 phase = getLockPhase();
    calldataarg args;
    f(e,args);
    assert phase == 4;
}

rule whichFunctionsOnlyPostSolver(method f)  filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector}{
    env e;

    uint8 phase = getLockPhase();
    calldataarg args;
    f(e,args);
    assert phase == 5;
}

rule whichFunctionsOnlyAllocateValue(method f) filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector} {
    env e;

    uint8 phase = getLockPhase();
    calldataarg args;
    f(e,args);
    assert phase == 6;
}

rule whichFunctionsOnlyPostOps(method f) filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector} {
    env e;

    uint8 phase = getLockPhase();
    calldataarg args;
    f(e,args);
    assert phase == 7;
}

rule whichFunctionsOnlyFullyLocked(method f) filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector} {
    env e;

    uint8 phase = getLockPhase();
    calldataarg args;
    f(e,args);
    assert phase == 8;
}

