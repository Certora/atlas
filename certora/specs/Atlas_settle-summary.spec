methods{ 
    function _.CALL_CONFIG() external => DISPATCHER(true);
    function GasAccounting._settle(GasAccounting.Context memory, uint256, address) internal returns (uint256, uint256) => invariantCheck();
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
// ghost to check invariant status inside metacall method
persistent ghost bool invariantHolds {
    init_state axiom invariantHolds == false;
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


/*----------------------------------------------------------------------------------------------------------------
                                                 CVL FUNCTIONS 
----------------------------------------------------------------------------------------------------------------*/

function invariantCheck() returns (uint256, uint256){
    invariantHolds = nativeBalances[currentContract] == 
    sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
    + currentContract.t_deposits - currentContract.t_withdrawals ? true : false;
    uint256 claimsPaidToBundler;
    uint256 netAtlasGasSurcharge;

    return (claimsPaidToBundler, netAtlasGasSurcharge);
}

/*----------------------------------------------------------------------------------------------------------------
                                                 RULES & INVARIANTS
----------------------------------------------------------------------------------------------------------------*/

// Atlas ETH balance = sum of AtlETH accounts {unbonded + bonded + unbonding} + cumulativeSurcharge + deposits - withdrawals
// STATUS: WIP
// 
rule atlasEthBalanceEqSumAccountsSurchargeTransient(){
    require nativeBalances[currentContract] == 
            sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
            + currentContract.t_deposits - currentContract.t_withdrawals;
    env e;
    calldataarg args;
    metacall(e, args);

    assert invariantHolds;
}