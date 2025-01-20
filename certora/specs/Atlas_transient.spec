import "./ERC20/erc20cvl.spec";
import "Atlas_ghostsAndHooks.spec";
using AtlasVerification as AtlasVerification;
using FastLaneOnlineControl as FastLaneOnlineControl;

methods{ 
   
    function _.getDAppConfig(Atlas.UserOperation) external => NONDET;
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
    function _.preOpsWrapper(Atlas.UserOperation) external => NONDET;
    function _.userWrapper(Atlas.UserOperation) external => NONDET;
    function _.getDAppSignatory() external => NONDET;
    function _.getL1FeeUpperBound() external => NONDET;
    function _.CALL_CONFIG() external => NONDET;
    function Base._control() internal returns (address)=> FastLaneOnlineControl;
    function _.isUnlocked() external => DISPATCHER(true);
    function _.postOpsWrapper(bool,bytes) external => NONDET;

    // getters
    function getLockEnv() external returns address envfree;
    function getLockCallConfig() external returns uint32 envfree;
    function getLockPhase() external returns uint8 envfree;
    function getActiveEnvironment() external returns address envfree;

    function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
    function Escrow._checkTrustedOpHash(Atlas.DAppConfig memory, bool, Atlas.UserOperation calldata, Atlas.SolverOperation calldata, uint256) internal returns uint256 => NONDET;


    function GasAccounting._updateAnalytics(Atlas.EscrowAccountAccessData memory, bool, uint256) internal => NONDET;

    function Factory._getOrCreateExecutionEnvironment(address, address, uint32) internal returns address => NONDET;

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
                                                 CVL FUNCTIONS
----------------------------------------------------------------------------------------------------------------*/


function settleCVL() returns (uint256, uint256){
    transientInvariantHolds = nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    assert withdrawals == 0 ;
    uint256 claimPaid;
    uint256 gasSurcharge;
    return (claimPaid, gasSurcharge);
}

/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/



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
