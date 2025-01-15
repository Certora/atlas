

import "./ERC20/erc20cvl.spec";
import "./ERC20/WETHcvl.spec";

// import "./MathSummaries.spec";
using AtlasVerification as AtlasVerification;
using Solver as solver;

methods{ 
    function _.CALL_CONFIG() external => DISPATCHER(true);
    // _.getCalldataCost() external => DISPATCHER(true);
    
    // unresolved external in _._ => DISPATCH [
    //     // FactoryLib.getOrCreateExecutionEnvironment(address, address, uint32, bytes32),
    //     // AtlasVerification.validateCalls(Atlas.DAppConfig, Atlas.UserOperation, 
    //                                     // Atlas.SolverOperation[], Atlas.DAppOperation, uint256, address, bool),
    //     // Atlas.execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool),
    //     // ExecutionEnvironment.solverPreTryCatch(uint256, Atlas.SolverOperation, bytes),
    //     // SolverBase.atlasSolverCall(address, address, address, uint256, bytes, bytes),
    //     Solver.atlasSolverCall(address, address, address, uint256, bytes, bytes)
    // ] default HAVOC_ALL;

    function _.getDAppConfig(Atlas.UserOperation) external => NONDET;
    function _.initialGasUsed(uint256) external => NONDET;
    function _._computeSalt(address, address, uint32) internal => NONDET;
    // function _bidFindingIteration(Atlas.Context memory, Atlas.DAppConfig memory, Atlas.UserOperation calldata, Atlas.SolverOperation[] calldata, bytes memory) internal returns uint256 => NONDET;
    // function _bidKnownIteration(Atlas.Context memory, Atlas.DAppConfig memory, Atlas.UserOperation calldata, Atlas.SolverOperation[] calldata, bytes memory) internal returns uint256 => NONDET;
    function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
    // function CallBits.exPostBids(uint32) internal returns bool => NONDET;
    // function AtlasVerification.validateCalls(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation,uint256, address, bool) external returns Atlas.ValidCallsResult => NONDET;
    function AtlasVerification.verifySolverOp(Atlas.SolverOperation, bytes32 ,uint256, address, bool) external returns uint256 => NONDET;
    // function _._executeUserOperation(Atlas.Context memory, Atlas.DAppConfig memory, Atlas.UserOperation calldata, bytes memory) internal  => NONDET;
    // function Escrow._executeUserOperation(Atlas.Context memory, Atlas.DAppConfig memory, Atlas.UserOperation calldata, bytes memory) internal returns bytes memory => _executeUserOperationCVL;
    function Escrow._checkSolverBidToken(address, address, uint256) internal returns uint256 => NONDET;
    function Escrow._validateSolverOpDeadline(Atlas.SolverOperation calldata, Atlas.DAppConfig memory) internal returns uint256 => NONDET;
    function Escrow._checkTrustedOpHash(Atlas.DAppConfig memory, bool, Atlas.UserOperation calldata, Atlas.SolverOperation calldata, uint256) internal returns uint256 => NONDET;
    function GasAccounting._updateAnalytics(Atlas.EscrowAccountAccessData memory, bool, uint256) internal => NONDET;
    function Factory._getOrCreateExecutionEnvironment(address, address, uint32) internal returns address => NONDET;
    function _.getCalldataCost(uint256) external => CONSTANT;
    function _.atlasSolverCall(address, address, address, uint256, bytes, bytes) external => DISPATCHER(true);
    function _.reconcile(uint256) external => DISPATCHER(true);
    
    // checking if this avoids the failed to locate function error
    // function _._allocateValueCall(address, uint256, bytes calldata) internal => NONDET;
    // function _._getCallConfig(uint32) internal => NONDET;

    // function _._getMimicCreationCode(address, address, uint32) internal => CONSTANT;
    
    // unresolved external in _._ => DISPATCH [
    //     // ExecutionEnvironment.preOpsWrapper(Atlas.UserOperation)
    //     ExecutionEnvironment.postOpsWrapper(bool, bytes),
        

    // ] default HAVOC_ALL;
    // function _.safeCall(address _target, uint256 _gas, uint256 _value, bytes memory _calldata) internal
    //     => cvlCall(_target, _gas, _value, _calldata) expect (bool);
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

// ghost bytes[8] _executeUserOperationCVL;

// ghost tracking the transient variable t_withdrawals
ghost uint256 withdrawals{
    init_state axiom withdrawals == 0;
}
// ghost tracking the transient variable t_deposits
ghost uint256 deposits{
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

/*----------------------------------------------------------------------------------------------------------------
                                                 CVL FUNCTIONS
----------------------------------------------------------------------------------------------------------------*/

// function cvlCall(address _target,uint256 _gas,uint256 _value, bytes _calldata) returns bool {
//     env e;
//     require e.msg.sender == currentContract;
//     require _target == solver;
//     bool success = _target.call(e, _calldata);

//     return success;
// }



/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/

// solverCall function
// https://prover.certora.com/output/11775/909fdf49ffbb40699f972f6029ba84fe?anonymousKey=4030e78a449d3678d87de9700a1d927208cc38af - with bid known path
// https://prover.certora.com/output/11775/230da475f45f459588a2fcd0b55cb5fa?anonymousKey=096ee1cb9a8e4a2b1507d553ec8982f3b28c1dfe - with bid find path
// https://prover.certora.com/output/11775/11c60f85e77542ae863cafaa13253fad?anonymousKey=2de67a4a68c3abe659e3596bcf93f9d0cf926cd7 - with coverage info and bid known path
// https://prover.certora.com/output/11775/14200893dcd74e668eb4b8ef20785b80?anonymousKey=4b06d9eab27ccb9bc40e33705f9aa3aa1069a8db - with coverage info and bid find path
// https://prover.certora.com/output/11775/f463977967a945b0b3e30b7d895bbd5c?anonymousKey=96b6b83928439f47b65150b7c2412ce5d805b4a6 - with dispatch list for atlasSolverCall
// https://prover.certora.com/output/11775/3da0cf7f05374c2682fa930f9c5d2e67?anonymousKey=a268c41044b196d682b3a309281f6e3716457207 - with munging to directly call solver.atlasSolverCall and DISPATCHER(true)
// https://prover.certora.com/output/11775/1c71bb8e298a415fa2f1d0c129ba4277?anonymousKey=4b85d3e88f47be5408313760ce0331ffb8c4a3dd - with reconcile dispatcher
// https://prover.certora.com/output/11775/be5dc544acc94263b494ae343c0cd46b?anonymousKey=a7ff246f8c997a27ee170f1d72b7f4acdd4430c5 - with safeTransfer summary
// https://prover.certora.com/output/11775/3d362db55c5d44f1a884e7a5fc32581d?anonymousKey=476f3f8a71136af0675e9ea3fd1a18476986f5f5 - with  internal summaries for safeTransfer/from
// https://prover.certora.com/output/11775/9ca3445b83a84254b1cce695834a37f7?anonymousKey=73986b92e9fd0373c7b4136401096ecb7fdd710b - with munging out .call in solverBase and weth withdraw summary
invariant atlasEthBalanceGeSumAccountsSurchargeSolverCall()
    nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
        filtered { f -> f.selector == sig:solverCall(Atlas.Context, Atlas.SolverOperation, uint256 ,bytes).selector}
        {
            preserved with (env e) {
                // assuming that Atlas is not the caller
                // require e.msg.sender != currentContract;
                }
        }

