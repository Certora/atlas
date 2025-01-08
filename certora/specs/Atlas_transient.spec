import "./ERC20/erc20cvl.spec";
import "Atlas_ghostsAndHooks.spec";

using AtlasVerification as AtlasVerification;
using FastLaneOnlineControl as FastLaneOnlineControl;

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
    function _.isUnlocked() external => DISPATCHER(true);

    
    // function _.allocateValue(address,uint256,bytes) external => NONDET; // SG xxx may contribute balance to Atlas, use better summary
    function _.postOpsWrapper(bool,bytes) external => NONDET;

    // getters
    function getLockEnv() external returns address envfree;
    function getLockCallConfig() external returns uint32 envfree;
    function getLockPhase() external returns uint8 envfree;

    // ND need to check these:
    //false would lead down the bidKnownIteration path which is simpler 
    function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
    // 
    function Escrow._checkTrustedOpHash(Atlas.DAppConfig memory, bool, Atlas.UserOperation calldata, Atlas.SolverOperation calldata, uint256) internal returns uint256 => NONDET;


    function GasAccounting._updateAnalytics(Atlas.EscrowAccountAccessData memory, bool, uint256) internal => NONDET;

    function Factory._getOrCreateExecutionEnvironment(address, address, uint32) internal returns address => NONDET;

    // need to fix:
    function _.solverPostTryCatch(Atlas.SolverOperation,bytes,Atlas.SolverTracker) external => NONDET;
    function _.solverPreTryCatch(uint256,Atlas.SolverOperation,bytes) external => NONDET;
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
    function _.solverPreTryCatch(
        uint256 bidAmount,
        Atlas.SolverOperation solverOp,
        bytes returnData
    ) external => DISPATCHER(true);
    unresolved external in _._ => DISPATCH(use_fallback=false) [
    ] default NONDET; 


    function _.atlasSolverCall(
        address solverOpFrom,
        address executionEnvironment,
        address bidToken,
        uint256 bidAmount,
        bytes solverOpData,
        bytes extraReturnData
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


/*----------------------------------------------------------------------------------------------------------------
                                                 CVL FUNCTIONS
----------------------------------------------------------------------------------------------------------------*/

/**
@title summary for settle function to check for the transient property 
**/
ghost bool transientInvariantHolds;
function settleCVL() returns (uint256, uint256){
    transientInvariantHolds = nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    uint256 claimPaid;
    uint256 gasSurcharge;
    return (claimPaid, gasSurcharge);
}

function dispatchDefault(){

}
/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/

/**
@todo - on which functions should this hold 
**/
invariant atlasEthBalanceGeSumAccountsSurchargeTransientMetacall()
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


rule atlasEthBalanceGeSumAccountsSurchargeTransientMetacallRule(){
    require withdrawals == 0; 
    require deposits == 0; 
    
    env e;
    require e.msg.sender != currentContract;
    
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge;

    calldataarg args;

    metacall(e, args);

    assert transientInvariantHolds;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}


/**

mutations 1:


mutation 2:
    function _borrow(uint256 amount) internal returns (bool valid) {
        if (amount == 0) return true;
        if (address(this).balance < amount) return false;
        // mutations - no update to t_withdrawals
        //t_withdrawals += amount; 