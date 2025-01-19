import "./ERC20/erc20cvl.spec";
// import "./MathSummaries.spec";
using AtlasVerification as AtlasVerification;
using FastLaneOnlineControl as FastLaneOnlineControl;
using SwapIntentDAppControl as SwapIntentDAppControl;
using V2DAppControl as V2DAppControl;
// using V2RewardDAppControl as V2RewardDAppControl;
using ExecutionEnvironment as ExecutionEnvironment;

methods{ 
    // view functions - same approximations 
    //function _.CALL_CONFIG() external => DISPATCHER(true);
    function _.getDAppConfig(Atlas.UserOperation) external => NONDET;
    // function _.initialGasUsed(uint256) external => NONDET;
    function _._computeSalt(address, address, uint32) internal => NONDET;
    function AtlasVerification.verifySolverOp(Atlas.SolverOperation, bytes32 ,uint256, address, bool) external returns uint256 => NONDET;
    function Escrow._checkSolverBidToken(address, address, uint256) internal returns uint256 => NONDET;
    function Escrow._validateSolverOpDeadline(Atlas.SolverOperation calldata, Atlas.DAppConfig memory) internal returns uint256 => NONDET;
    function _.getCalldataCost(uint256 l) external => calldataCostGhost[l] expect (uint256) ALL;
    function _._getCalldataCost(uint256 l) internal => calldataCostGhost[l] expect (uint256); // why ext summary wasn't applied? because we needed all. but the wrapper also isn't needed

    function _.initialGasUsed(uint256 l) external => initialGasUsed[l] expect (uint256) ALL;
    function GasAccounting._settle(Atlas.Context memory, uint256, address) internal returns (uint256, uint256) => settleCVL();
    function Escrow.errorSwitch(bytes4) internal returns (uint256) => NONDET;
    function EscrowBits.canExecute(uint256) internal returns (bool) => ALWAYS(true);
    // function Escrow._solverOpWrapper(Atlas.Context memory, Atlas.SolverOperation calldata, uint256, uint256, bytes memory) internal returns (uint256, Atlas.SolverTracker memory) => nothingSolverOp();

    function _.preOpsWrapper(Atlas.UserOperation) external => NONDET;
    function _.userWrapper(Atlas.UserOperation) external => NONDET;
    function _.getDAppSignatory() external => NONDET;
    function _.getL1FeeUpperBound() external => NONDET;
    function _.CALL_CONFIG() external => NONDET;
    function Base._control() internal returns (address)=> FastLaneOnlineControl;

    
    // function _.allocateValue(address,uint256,bytes) external => NONDET; // SG xxx may contribute balance to Atlas, use better summary
    function _.postOpsWrapper(bool,bytes) external => NONDET;
    // function _._postSolverCall(Atlas.SolverOperation calldata, bytes calldata) internal => DISPATCHER(true);
    // function _._preOpsCall(Atlas.UserOperation calldata) internal => NONDET;
    function _._checkUserOperation(Atlas.UserOperation memory) internal => NONDET;
    function _.transferUserERC20(address, address, uint256, address, address) external => DISPATCHER(true);
    // function _._postSolverCall(Atlas.SolverOperation, bytes) internal => DISPATCHER(true);

    // getters
    function getLockEnv() external returns address envfree;
    function getLockCallConfig() external returns uint32 envfree;
    function getLockPhase() external returns uint8 envfree;
    function getActiveEnvironment() external returns address envfree;
    function Escrow.userWrapperEmpty() internal returns (bool, bytes memory) => userWrapperCVL();

    // ND need to check these:
    //false would lead down the bidKnownIteration path which is simpler 
    function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
    // 
    function Escrow._checkTrustedOpHash(Atlas.DAppConfig memory, bool, Atlas.UserOperation calldata, Atlas.SolverOperation calldata, uint256) internal returns uint256 => NONDET;


    function GasAccounting._updateAnalytics(Atlas.EscrowAccountAccessData memory, bool, uint256) internal => NONDET;

    function Factory._getOrCreateExecutionEnvironment(address, address, uint32) internal returns address => NONDET;

    // need to fix:
    //function _.solverPostTryCatch(Atlas.SolverOperation,bytes,Atlas.SolverTracker) external => NONDET;
    //function _.solverPreTryCatch(uint256,Atlas.SolverOperation,bytes) external => NONDET;
    //function _.atlasSolverCall(address,address,address,uint256,bytes,bytes) external => NONDET;

    unresolved external in _._(address, uint256, bytes) => DISPATCH [
        FastLaneOnlineControl.allocateValueCall(address, uint256, bytes)
    ] default HAVOC_ALL;

    unresolved external in _.solverPreTryCatch(uint256, Atlas.SolverOperation, bytes) => DISPATCH [
        FastLaneOnlineControl.preSolverCall(Atlas.SolverOperation,bytes)
    ] default HAVOC_ALL;

    unresolved external in _.preOpsWrapper(Atlas.UserOperation) => DISPATCH [
        FastLaneOnlineControl.preOpsCall(Atlas.UserOperation)
    ] default HAVOC_ALL;
    
    unresolved external in _.postOpsWrapper(bool, bytes) => DISPATCH [
        FastLaneOnlineControl.postOpsCall(bool, bytes)
    ] default HAVOC_ALL;
    
    unresolved external in _.userWrapper(Atlas.UserOperation) => DISPATCH [
        FastLaneOnlineControl.postOpsCall(bool, bytes)
    ] default HAVOC_ALL;

    unresolved external in _._allocateValue(Atlas.Context, Atlas.DAppConfig, uint256, bytes) => DISPATCH [
        ExecutionEnvironment.allocateValue(address, uint256, bytes)
    ] default HAVOC_ALL;
    
    unresolved external in _._allocateValue(Atlas.Context, Atlas.DAppConfig, uint256, bytes) => DISPATCH [
        ExecutionEnvironment.allocateValue(address, uint256, bytes)
    ] default NONDET;

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


    // limiting to without delegate call
    function CallBits.needsPostSolverCall(uint32 callConfig) internal returns (bool) => ALWAYS(false) ;

    function CallBits.needsPostOpsCall(uint32 callConfig) internal returns (bool)  => ALWAYS(false) ;

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

// ghost tracking the transient variable t_withdrawals
ghost uint256 withdrawals {
    init_state axiom withdrawals == 0;
}
// ghost tracking the transient variable t_deposits
ghost uint256 deposits {
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
        require withdrawals == v; 
    if (loc == 8) 
        require deposits == v; 
} 

persistent ghost bool called_extcall;

// We are hooking here on "CALL" opcodes in order to capture if there was a storage access before or/and after a call
hook CALL(uint g, address addr, uint value, uint argsOffset, uint argsLength, uint retOffset, uint retLength) uint rc {

    called_extcall = called_extcall || addr != currentContract;
}

/*----------------------------------------------------------------------------------------------------------------
                                                 CVL FUNCTIONS
----------------------------------------------------------------------------------------------------------------*/


function settleCVL() returns (uint256, uint256){
    transientInvariantHolds = nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    assert withdrawals == 0 ;
    uint256 claimPaid;
    uint256 gasSurcharge;
    return (claimPaid, gasSurcharge);
}

function dispatchDefault(){

}

function userWrapperCVL() returns (bool, bytes){
    bool _success;
    bytes _data;

    return (_success, _data);
}

// functions that are interesting for the invariant
// function reentrancyFunction1(method f) {
//     require f.selector == sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool).selector ||
//             f.selector == sig:getExecutionEnvironment(address,address).selector ||
//             f.selector == sig:createExecutionEnvironment(address,address).selector ||
//             f.selector == sig:contribute().selector ||
//             f.selector == sig:contribute().selector ||
//             f.selector == sig:withdrawSurcharge().selector ||
//             f.selector == sig:becomeSurchargeRecipient().selector ||
//             f.selector == sig:getActiveEnvironment().selector ||
//             f.selector == sig:getLockCallConfig().selector ||
//             f.selector == sig:getLockPhase().selector ||
//             f.selector == sig:getLockEnv().selector ||
//             f.selector == sig:reconcile(uint256).selector ||
//             f.selector == sig:borrow(uint256).selector ||
//             f.selector == sig:transferSurchargeRecipient(address).selector ||
//             f.selector == sig:solverCall(Atlas.Context, Atlas.SolverOperation, uint256, bytes).selector ||
//             f.selector == sig:transferUserERC20(address,address,uint256,address,address).selector ||
//             f.selector == sig:transferDAppERC20(address,address,uint256,address,address).selector ||
//             f.selector == sig:ExecutionEnvironment.allocateValue(address,uint256,bytes).selector ||
//             f.selector == sig:ExecutionEnvironment.solverPreTryCatch(uint256,Atlas.SolverOperation,bytes).selector ||
//             f.selector == sig:ExecutionEnvironment.solverPostTryCatch(Atlas.SolverOperation, bytes, Atlas.SolverTracker).selector ||
//             f.selector == sig:ExecutionEnvironment.preOpsWrapper(Atlas.UserOperation).selector ||
//             f.selector == sig:ExecutionEnvironment.userWrapper(Atlas.UserOperation).selector ||
//             f.selector == sig:ExecutionEnvironment.withdrawERC20(address,uint256).selector ||
//             f.selector == sig:ExecutionEnvironment.withdrawEther(uint256).selector ||
//             f.selector == sig:ExecutionEnvironment.postOpsWrapper(bool,bytes).selector ||
//             f.selector == sig:FastLaneOnlineControl.preSolverCall(Atlas.SolverOperation,bytes).selector ||
//             f.selector == sig:FastLaneOnlineControl.postSolverCall(Atlas.SolverOperation,bytes).selector ||
//             f.selector == sig:FastLaneOnlineControl.preOpsCall(Atlas.UserOperation).selector ||
//             f.selector == sig:FastLaneOnlineControl.postOpsCall(bool,bytes).selector ||
//             f.selector == sig:FastLaneOnlineControl.allocateValueCall(address,uint256,bytes).selector;
//     }

// role handover or other no so interesting state change functions
// function reentrancyFunction2(method f) {
//     require
//             f.selector == sig:AtlasVerification.removeSignatory(address,address).selector ||
//             f.selector == sig:AtlasVerification.addSignatory(address,address).selector ||
//             f.selector == sig:AtlasVerification.initializeGovernance(address).selector ||
//             f.selector == sig:AtlasVerification.disableDApp(address).selector ||
//             f.selector == sig:BaseGasCalculator.renounceOwnership().selector ||
//             f.selector == sig:BaseGasCalculator.setCalldataLengthOffset(int256).selector ||
//             f.selector == sig:BaseGasCalculator.transferOwnership(address).selector ||
//             f.selector == sig:DAppIntegration.removeSignatory(address,address).selector ||
//             f.selector == sig:DAppIntegration.addSignatory(address,address).selector ||
//             f.selector == sig:DAppIntegration.initializeGovernance(address).selector ||
//             f.selector == sig:DAppIntegration.disableDApp(address).selector ||
//             f.selector == sig:FastLaneOnlineControl.acceptGovernance().selector ||
//             f.selector == sig:FastLaneOnlineControl.transferGovernance(address).selector;
//     }


definition reentrancyFunction1(method f) returns bool =
	        f.selector == sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool).selector ||
            f.selector == sig:getExecutionEnvironment(address,address).selector ||
            f.selector == sig:createExecutionEnvironment(address,address).selector ||
            f.selector == sig:contribute().selector ||
            f.selector == sig:contribute().selector ||
            f.selector == sig:withdrawSurcharge().selector ||
            f.selector == sig:becomeSurchargeRecipient().selector ||
            f.selector == sig:getActiveEnvironment().selector ||
            f.selector == sig:getLockCallConfig().selector ||
            f.selector == sig:getLockPhase().selector ||
            f.selector == sig:getLockEnv().selector ||
            f.selector == sig:reconcile(uint256).selector ||
            f.selector == sig:borrow(uint256).selector ||
            f.selector == sig:transferSurchargeRecipient(address).selector ||
            f.selector == sig:solverCall(Atlas.Context, Atlas.SolverOperation, uint256, bytes).selector ||
            f.selector == sig:transferUserERC20(address,address,uint256,address,address).selector ||
            f.selector == sig:transferDAppERC20(address,address,uint256,address,address).selector ||
            f.selector == sig:ExecutionEnvironment.allocateValue(address,uint256,bytes).selector ||
            f.selector == sig:ExecutionEnvironment.solverPreTryCatch(uint256,Atlas.SolverOperation,bytes).selector ||
            f.selector == sig:ExecutionEnvironment.solverPostTryCatch(Atlas.SolverOperation, bytes, Atlas.SolverTracker).selector ||
            f.selector == sig:ExecutionEnvironment.preOpsWrapper(Atlas.UserOperation).selector ||
            f.selector == sig:ExecutionEnvironment.userWrapper(Atlas.UserOperation).selector ||
            f.selector == sig:ExecutionEnvironment.withdrawERC20(address,uint256).selector ||
            f.selector == sig:ExecutionEnvironment.withdrawEther(uint256).selector ||
            f.selector == sig:ExecutionEnvironment.postOpsWrapper(bool,bytes).selector ||
            f.selector == sig:FastLaneOnlineControl.preSolverCall(Atlas.SolverOperation,bytes).selector ||
            f.selector == sig:FastLaneOnlineControl.postSolverCall(Atlas.SolverOperation,bytes).selector ||
            f.selector == sig:FastLaneOnlineControl.preOpsCall(Atlas.UserOperation).selector ||
            f.selector == sig:FastLaneOnlineControl.postOpsCall(bool,bytes).selector ||
            f.selector == sig:FastLaneOnlineControl.allocateValueCall(address,uint256,bytes).selector;
	
definition reentrancyFunction2(method f) returns bool =
	        f.selector == sig:AtlasVerification.removeSignatory(address,address).selector ||
            f.selector == sig:AtlasVerification.addSignatory(address,address).selector ||
            f.selector == sig:AtlasVerification.initializeGovernance(address).selector ||
            f.selector == sig:AtlasVerification.disableDApp(address).selector ||
            f.selector == sig:BaseGasCalculator.renounceOwnership().selector ||
            f.selector == sig:BaseGasCalculator.setCalldataLengthOffset(int256).selector ||
            f.selector == sig:BaseGasCalculator.transferOwnership(address).selector ||
            f.selector == sig:DAppIntegration.removeSignatory(address,address).selector ||
            f.selector == sig:DAppIntegration.addSignatory(address,address).selector ||
            f.selector == sig:DAppIntegration.initializeGovernance(address).selector ||
            f.selector == sig:DAppIntegration.disableDApp(address).selector ||
            f.selector == sig:FastLaneOnlineControl.acceptGovernance().selector ||
            f.selector == sig:FastLaneOnlineControl.transferGovernance(address).selector;
	
/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/


rule whoCanChangePhaseFromZero(method f, env e) filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    // require e.msg.sender != currentContract;
    // require e.msg.sender != getActiveEnvironment();
    require _phase == 0;

    calldataarg args;
    f(e, args);
    
    uint8 phase_ = getLockPhase();

    assert _phase == phase_;
    // satisfy storage changes
}

rule whoCanChangeStorageInZeroPhase(method f, env e) filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    require _phase == 0;

    storage init = lastStorage;
    
    calldataarg args;
    f(e, args);
    
    storage final = lastStorage;
    
    satisfy final != init;
}

// reentrancy functions transient invariant check

// execute function
rule executeTransientInv(env e){
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    execute(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule solverCallTransientInv(env e){
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    solverCall(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule internalFuncTransientInv1(env e, method f) filtered{f -> f.selector == sig:getExecutionEnvironment(address,address).selector ||
            f.selector == sig:createExecutionEnvironment(address,address).selector ||
            f.selector == sig:contribute().selector ||
            f.selector == sig:contribute().selector ||
            f.selector == sig:withdrawSurcharge().selector ||
            f.selector == sig:becomeSurchargeRecipient().selector ||
            f.selector == sig:getActiveEnvironment().selector ||
            f.selector == sig:getLockCallConfig().selector ||
            f.selector == sig:getLockPhase().selector ||
            f.selector == sig:getLockEnv().selector ||
            f.selector == sig:reconcile(uint256).selector ||
            f.selector == sig:borrow(uint256).selector ||
            f.selector == sig:transferSurchargeRecipient(address).selector ||
            f.selector == sig:transferUserERC20(address,address,uint256,address,address).selector ||
            f.selector == sig:transferDAppERC20(address,address,uint256,address,address).selector}
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    require e.msg.sender != currentContract;

    calldataarg args;
    f(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule internalFuncTransientInv2(env e, method f) filtered{f -> f.selector == sig:ExecutionEnvironment.allocateValue(address,uint256,bytes).selector ||
            f.selector == sig:ExecutionEnvironment.withdrawERC20(address,uint256).selector ||
            f.selector == sig:ExecutionEnvironment.withdrawEther(uint256).selector ||
            f.selector == sig:ExecutionEnvironment.postOpsWrapper(bool,bytes).selector ||
            f.selector == sig:FastLaneOnlineControl.postOpsCall(bool,bytes).selector ||
            f.selector == sig:FastLaneOnlineControl.allocateValueCall(address,uint256,bytes).selector
            }
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    if (f.selector == sig:FastLaneOnlineControl.postOpsCall(bool,bytes).selector) {
    // for postOpsCall
    // require balance - e.msg.value >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    require e.msg.value == 0;

    }
    calldataarg args;
    f(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule internalFuncTransientInv3(env e, method f) filtered{f -> f.selector == sig:AtlasVerification.removeSignatory(address,address).selector ||
            f.selector == sig:AtlasVerification.addSignatory(address,address).selector ||
            f.selector == sig:AtlasVerification.initializeGovernance(address).selector ||
            f.selector == sig:AtlasVerification.disableDApp(address).selector ||
            f.selector == sig:BaseGasCalculator.renounceOwnership().selector ||
            f.selector == sig:BaseGasCalculator.setCalldataLengthOffset(int256).selector ||
            f.selector == sig:BaseGasCalculator.transferOwnership(address).selector ||
            f.selector == sig:DAppIntegration.removeSignatory(address,address).selector ||
            f.selector == sig:DAppIntegration.addSignatory(address,address).selector ||
            f.selector == sig:DAppIntegration.initializeGovernance(address).selector ||
            f.selector == sig:DAppIntegration.disableDApp(address).selector ||
            f.selector == sig:FastLaneOnlineControl.acceptGovernance().selector ||
            f.selector == sig:FastLaneOnlineControl.transferGovernance(address).selector
            }
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    f(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule solverPreTryCatchTransientInv(env e)
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    require e.msg.value == 0;
    calldataarg args;
    ExecutionEnvironment.solverPreTryCatch(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule solverPostTryCatchTransientInv(env e)
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    require e.msg.value == 0;

    calldataarg args;
    ExecutionEnvironment.solverPostTryCatch(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule preOpsWrapperTransientInv(env e)
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    ExecutionEnvironment.preOpsWrapper(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule userWrapperTransientInv(env e)
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    Atlas.UserOperation userOp;
    userWrapperHarness(e, userOp);
    // ExecutionEnvironment.userWrapper(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule preSolverCallTransientInv(env e)
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    require e.msg.value == 0;

    calldataarg args;
    FastLaneOnlineControl.preSolverCall(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule postSolverCallTransientInv(env e)
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    require e.msg.value == 0;

    calldataarg args;
    SwapIntentDAppControl.postSolverCall(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule preOpsCallTransientInv(env e)
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    require e.msg.value == 0;
    calldataarg args;
    V2DAppControl.preOpsCall(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}







rule internalFunctionsTransientInvariant1(method f)
{
    require reentrancyFunction1(f);
    env e;
    
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    f(e, args);

    assert transientInvariantHolds;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule internalFunctionsTransientInvariant2(method f)
{
    require reentrancyFunction2(f);
    env e;
    
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    f(e, args);

    assert transientInvariantHolds;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

rule whoCanChangeStorageInZeroPhaseSenderNotCurrentCon(method f, env e) 
    // filtered{f -> 
        // f.selector == metacall((address,address,uint256,uint256,uint256,uint256,uint256,address,address,uint32,address,bytes,bytes),(address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes)[],(address,address,uint256,uint256,address,address,bytes32,bytes32,bytes),address) ||
        // f.selector == execute((address,uint32,address,uint32),(address,address,uint256,uint256,uint256,uint256,uint256,address,address,uint32,address,bytes,bytes),(address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes)[],address,address,bytes32,bool) ||
        // f.selector == contribute() ||
        // f.selector == deposit() ||
        // f.selector == withdrawSurcharge() ||
        // f.selector == becomeSurchargeRecipient() ||
        // f.selector == unbond(uint256) ||
        // f.selector == depositAndBond(uint256) ||
        // f.selector == redeem(uint256) ||
        // f.selector == borrow(uint256) ||
        // f.selector == bond(uint256) ||
        // f.selector == withdraw(uint256) ||
        // f.selector == transferSurchargeRecipient(address) ||
        // f.selector == solverCall((bytes32,address,uint24,uint8,uint8,uint8,uint8,bool,bool,bool,bool,address),(address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes),uint256,bytes) ||
        // f.selector == removeSignatory(address,address) ||
        // f.selector == changeDAppGovernance(address,address) ||
        // f.selector == addSignatory(address,address) ||
        // f.selector == initializeGovernance(address) ||
        // f.selector == disableDApp(address) ||
        // f.selector == renounceOwnership() ||
        // f.selector == setCalldataLengthOffset(int256) ||
        // f.selector == transferOwnership(address) ||
        // f.selector == removeSignatory(address,address) ||
        // f.selector == changeDAppGovernance(address,address) ||
        // f.selector == addSignatory(address,address) ||
        // f.selector == initializeGovernance(address) ||
        // f.selector == disableDApp(address) ||
        // f.selector == allocateValue(address,uint256,bytes) ||
        // f.selector == solverPreTryCatch(uint256,(address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes),bytes) ||
        // f.selector == solverPostTryCatch((address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes),bytes,(uint256,uint256,uint256,bool,bool)) ||
        // f.selector == userWrapper((address,address,uint256,uint256,uint256,uint256,uint256,address,address,uint32,address,bytes,bytes)) ||
        // f.selector == withdrawEther(uint256) ||
        // f.selector == getOrCreateExecutionEnvironment(address,address,uint32,bytes32) ||
        // f.selector == acceptGovernance() ||
        // f.selector == transferGovernance(address)
// }
{
    uint8 _phase = getLockPhase();
    require _phase == 0;
    require e.msg.sender != currentContract;
    // require e.msg.sender != getActiveEnvironment();

    storage init = lastStorage;
    
    calldataarg args;
    f(e, args);
    
    storage final = lastStorage;
    
    satisfy final != init;
}



rule innerFunctions0(method f, env e)filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    
    require _phase == require_uint8(Atlas.ExecutionPhase.Uninitialized);
    
    calldataarg args;
    f(e, args);

    // assert false;
    satisfy true;
}

rule innerFunctions1(method f, env e)filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    
    require _phase == require_uint8(Atlas.ExecutionPhase.PreOps);
    
    calldataarg args;
    f(e, args);

    // assert false;
    satisfy true;
}

rule innerFunctions2(method f, env e)filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    
    require _phase == require_uint8(Atlas.ExecutionPhase.UserOperation);
    
    calldataarg args;
    f(e, args);

    // assert false;
    satisfy true;
}
rule innerFunctions3(method f, env e)filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    
    require _phase == require_uint8(Atlas.ExecutionPhase.PreSolver);
    
    calldataarg args;
    f(e, args);

    // assert false;
    satisfy true;
}
rule innerFunctions4(method f, env e)filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    
    require _phase == require_uint8(Atlas.ExecutionPhase.SolverOperation);
    
    calldataarg args;
    f(e, args);

    // assert false;
    satisfy true;
}
rule innerFunctions5(method f, env e)filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    
    require _phase == require_uint8(Atlas.ExecutionPhase.PostSolver);
    
    calldataarg args;
    f(e, args);

    // assert false;
    satisfy true;
}
rule innerFunctions6(method f, env e)filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    
    require _phase == require_uint8(Atlas.ExecutionPhase.AllocateValue);
    
    calldataarg args;
    f(e, args);

    // assert false;
    satisfy true;
}
rule innerFunctions7(method f, env e)filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    
    require _phase == require_uint8(Atlas.ExecutionPhase.PostOps);
    
    calldataarg args;
    f(e, args);

    // assert false;
    satisfy true;
}
rule innerFunctions8(method f, env e)filtered{f -> !f.isView}
{
    uint8 _phase = getLockPhase();
    
    require _phase == require_uint8(Atlas.ExecutionPhase.FullyLocked);
    
    calldataarg args;
    f(e, args);

    // assert false;
    satisfy true;
}


// prove that metacall can only be called in phase 0 and at the end of it phase is 0


