import "./ERC20/erc20cvl.spec";


/*----------------------------------------------------------------------------------------------------------------
                                                 GHOSTS & HOOKS 
----------------------------------------------------------------------------------------------------------------*/

ghost mapping(uint256 => uint256) calldataCostGhost;


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


/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/


/**
@title settle final accounting leaves the protocol in a solvent ETH balance:
Atlas ETH balance = sum of AtlETH accounts {unbonded + bonded + unbonding}
									+ cumulativeSurcharge 

**/
rule atlasEthBalanceGeSumAccountsSurchargeSettleRule(){
    
    
    env e;
    require e.msg.sender != currentContract;
    require sumOfBonded >= 0 && sumOfUnbonded >= 0 && sumOfUnbonding >=0;
    
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals ;

    calldataarg args;

    settle(e, args);

    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge  ;
    satisfy true;
}

