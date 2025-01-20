import "./ERC20/erc20cvl.spec";
import "./Atlas_ghostsAndHooks.spec";
using AtlasVerification as AtlasVerification;
using FastLaneOnlineControl as FastLaneOnlineControl;
using SwapIntentDAppControl as SwapIntentDAppControl;
using V2DAppControl as V2DAppControl;
using ExecutionEnvironment as ExecutionEnvironment;
using FactoryLib as FactoryLib;

methods{ 
    // view functions - same approximations 
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

    function _.postOpsWrapper(bool,bytes) external => NONDET;
    function _._checkUserOperation(Atlas.UserOperation memory) internal => NONDET;
    function _.transferUserERC20(address, address, uint256, address, address) external => DISPATCHER(true);

    // getters
    function getLockEnv() external returns address envfree;
    function getLockCallConfig() external returns uint32 envfree;
    function getLockPhase() external returns uint8 envfree;
    function getActiveEnvironment() external returns address envfree;
    function Escrow.userWrapperEmpty() internal returns (bool, bytes memory) => userWrapperCVL();

    function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
    // 
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
                                                 CVL FUNCTIONS
----------------------------------------------------------------------------------------------------------------*/


function settleCVL() returns (uint256, uint256){
    transientInvariantHolds = nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    uint256 claimPaid;
    uint256 gasSurcharge;
    return (claimPaid, gasSurcharge);
}



function userWrapperCVL() returns (bool, bytes){
    bool _success;
    bytes _data;

    return (_success, _data);
}


/// Functions that can only be called in reentrant mode 
definition reentrancyOnlyFunctions(method f) returns bool =
	        f.selector == sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool).selector ||
            f.selector == sig:contribute().selector ||
            f.selector == sig:contribute().selector ||
            f.selector == sig:withdrawSurcharge().selector ||
            f.selector == sig:becomeSurchargeRecipient().selector ||
            f.selector == sig:getActiveEnvironment().selector ||
            f.selector == sig:getLockCallConfig().selector ||
            f.selector == sig:getLockPhase().selector ||
            f.selector == sig:getLockEnv().selector ||
            f.selector == sig:reconcile(uint256).selector ||
            f.selector == sig:transferSurchargeRecipient(address).selector ||
            f.selector == sig:solverCall(Atlas.Context, Atlas.SolverOperation, uint256, bytes).selector ||
            f.selector == sig:transferUserERC20(address,address,uint256,address,address).selector ||
            f.selector == sig:transferDAppERC20(address,address,uint256,address,address).selector ||
            f.selector == sig:ExecutionEnvironment.allocateValue(address,uint256,bytes).selector ||
            f.selector == sig:ExecutionEnvironment.solverPreTryCatch(uint256,Atlas.SolverOperation,bytes).selector ||
            f.selector == sig:ExecutionEnvironment.solverPostTryCatch(Atlas.SolverOperation, bytes, Atlas.SolverTracker).selector ||
            f.selector == sig:ExecutionEnvironment.preOpsWrapper(Atlas.UserOperation).selector ||
            f.selector == sig:ExecutionEnvironment.userWrapper(Atlas.UserOperation).selector ||
            f.selector == sig:ExecutionEnvironment.postOpsWrapper(bool,bytes).selector ||
            f.selector == sig:ExecutionEnvironment.withdrawERC20(address,uint256).selector ||
            f.selector == sig:ExecutionEnvironment.withdrawEther(uint256).selector ||
            f.selector == sig:FastLaneOnlineControl.preSolverCall(Atlas.SolverOperation,bytes).selector ||
            f.selector == sig:FastLaneOnlineControl.postSolverCall(Atlas.SolverOperation,bytes).selector ||
            f.selector == sig:FastLaneOnlineControl.preOpsCall(Atlas.UserOperation).selector ||
            f.selector == sig:FastLaneOnlineControl.postOpsCall(bool,bytes).selector ||
            f.selector == sig:FastLaneOnlineControl.allocateValueCall(address,uint256,bytes).selector;


definition reentrancyAndTopLevelFunctions(method f) returns bool = 
            f.selector == sig:borrow(uint256).selector ||
            f.selector == sig:AtlasHarness.bond(uint256).selector ||
            f.selector == sig:AtlasVerification.removeSignatory(address,address).selector ||
            f.selector == sig:AtlasVerification.addSignatory(address,address).selector ||
            f.selector == sig:AtlasVerification.initializeGovernance(address).selector ||
            f.selector == sig:AtlasVerification.disableDApp(address).selector ||
            f.selector == sig:AtlasVerification.changeDAppGovernance(address,address).selector ||
            f.selector == sig:BaseGasCalculator.renounceOwnership().selector ||
            f.selector == sig:BaseGasCalculator.setCalldataLengthOffset(int256).selector ||
            f.selector == sig:BaseGasCalculator.transferOwnership(address).selector ||
            f.selector == sig:DAppIntegration.removeSignatory(address,address).selector ||
            f.selector == sig:DAppIntegration.addSignatory(address,address).selector ||
            f.selector == sig:DAppIntegration.initializeGovernance(address).selector ||
            f.selector == sig:DAppIntegration.disableDApp(address).selector ||
            f.selector == sig:FastLaneOnlineControl.acceptGovernance().selector ||
            f.selector == sig:FastLaneOnlineControl.transferGovernance(address).selector ||
            f.selector == sig:FactoryLib.getOrCreateExecutionEnvironment(address,address,uint32,bytes32).selector ||
            f.selector == sig:depositAndBond(uint256).selector ||
            f.selector == sig:deposit().selector ||
            f.isFallback;


definition reentrancyFunction(method f) returns bool = reentrancyOnlyFunctions(f) ||  reentrancyAndTopLevelFunctions(f);

definition atlasContracts(address c) returns bool = 
        c == currentContract /*Atlas */ ||
        c == ExecutionEnvironment || 
        c == ExecutionEnvironment.SOURCE ||
        c == getActiveEnvironment() || 
        c == currentContract.S_surchargeRecipient;
/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/


/**
Prove Top level functions - that can change a storage in phase 0 
**/
rule whoCanChangeStorageInZeroPhase(method f, env e) 
        filtered{f -> !f.isView && !reentrancyFunction(f)||
        //behaves as getters:
        f.selector == sig:getExecutionEnvironment(address,address).selector ||
        f.selector == sig:createExecutionEnvironment(address,address).selector 
          }
{
    uint8 _phase = getLockPhase();
    require _phase == 0;

    storage init = lastStorage;
    
    calldataarg args;
    f(e, args);
    
    storage final = lastStorage;
    
    satisfy final != init && !atlasContracts(e.msg.sender);
}

/**
Prove that reentrant functions can only be executed in a non phase 0 or by authorized contracts or that they just don't change the state 
**/
rule reentrancyOnly(method f, env e) filtered{f -> !f.isView && !reentrancyFunction(f)}
{
    uint8 _phase = getLockPhase();
    storage init = lastStorage;

    calldataarg args;
    f(e, args);

    storage final = lastStorage;
    
    assert _phase > 0 || atlasContracts(e.msg.sender) || e.msg.sender == msgSenderCalledMetaCall;

}

/**
Prove that not reentrant functions (top level functions) can only be executed in a phase 0 or
the are view functions  
**/
rule topLevelFunctions(method f, env e) filtered{f -> !f.isView && !reentrancyFunction(f)}
{
    uint8 _phase = getLockPhase();
    storage init = lastStorage;

    // assume we are not within a metacall 
    require msgSenderCalledMetaCall == 0 ;
    require e.msg.sender != 0 ;
    
    calldataarg args;
    f(e, args);

    storage final = lastStorage;
    
    
    assert _phase == 0 || init == final ;

}
/**
@title top level functions should preserve the total eth balance with respect to internal accounting  
@dev metacall() is proved separately 
**/
invariant solvency()
    nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge 
    filtered {f -> f.selector != sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector &&
    !reentrancyOnlyFunctions(f) }
    {
        preserved with (env e) {
            require !atlasContracts(e.msg.sender) ;
        }
    }


/**
@title reentrant functions preserving the transient invariant
**/
// execute function
rule executeTransientInv(env e){
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    execute(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

// solverCall
rule solverCallTransientInv(env e){
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    solverCall(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

// reentrant functions set1
rule internalFuncTransientInv1(env e, method f) filtered{f -> 
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
            f.selector == sig:transferUserERC20(address,address,uint256,address,address).selector ||
            f.selector == sig:transferDAppERC20(address,address,uint256,address,address).selector || 
            f.selector == sig:FactoryLib.getOrCreateExecutionEnvironment(address,address,uint32,bytes32).selector ||
            f.selector == sig:depositAndBond(uint256).selector ||
            f.selector == sig:deposit().selector ||
            ( f.isFallback && f.contract == FactoryLib)       
            }
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    require e.msg.sender != currentContract;

    calldataarg args;
    f(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

// reentrant functions set2
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

// reentrant functions set3
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

// reentrant functions set4
rule internalFuncTransientInv4(env e, method f) filtered{f -> f.selector == sig:AtlasHarness.bond(uint256).selector ||
                    f.selector == sig:AtlasVerification.removeSignatory(address,address).selector ||
                    f.selector == sig:AtlasVerification.changeDAppGovernance(address,address).selector ||
                    f.selector == sig:transferDAppERC20(address,address,uint256,address,address).selector ||
                    f.selector == sig:ExecutionEnvironment.allocateValue(address,uint256,bytes).selector
            }
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    f(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

// solverPreTryCatch 
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

// solverPostTryCatch
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

// preOpsWrapper
rule preOpsWrapperTransientInv(env e)
{
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    calldataarg args;
    ExecutionEnvironment.preOpsWrapper(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
    satisfy deposits > 0; 
    satisfy withdrawals > 0;
}

// userWrapper
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

// preSolverCall
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

// postSolverCall
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

// preOpsCall
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