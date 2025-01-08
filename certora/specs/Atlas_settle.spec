import "./ERC20/erc20cvl.spec";
import "Atlas_ghostsAndHooks.spec";

/*----------------------------------------------------------------------------------------------------------------
                                                 RULES
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


/** @dev  
Rule atlasEthBalanceGeSumAccountsSurchargeSettleRule Proved : https://prover.certora.com/output/40726/7eea9911674445cd91778b8544dbdd0d/?anonymousKey=4c16f9414a56f796ed6c3608df28fa926b5d036b
checked with two mutations:
https://prover.certora.com/output/40726/999ac9931bf14d5b9629ed3e974a17be/?anonymousKey=aade0ef58628f008403a1893792410ebed0b4c52
        //mutation1 flip _amountSolverPays and _amountSolverReceives
        if (_deposits < _withdrawals) {
            //_amountSolverPays = _withdrawals - _deposits;
            _amountSolverReceives = _withdrawals - _deposits;
        } else {
            //_amountSolverReceives = _deposits - _withdrawals;
            _amountSolverPays = _deposits - _withdrawals;
        }
2.  https://prover.certora.com/output/40726/ecb16e76252f4d46ad634f985ff0b449/?anonymousKey=cecf116e45ea06e6c64bdda8ba494529b7007034
        // mutation 2 - make sure we reach this option - pay it all
        if (claimsPaidToBundler != 0) SafeTransferLib.safeTransferETH(gasRefundBeneficiary, address(this).balance);
        //if (claimsPaidToBundler != 0) SafeTransferLib.safeTransferETH(gasRefundBeneficiary, claimsPaidToBundler); 

*/ 