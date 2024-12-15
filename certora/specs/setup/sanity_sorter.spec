import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";


methods{ 
    function _.getBidFormat(DAppControl.UserOperation) external => DISPATCHER(true);
    function _.getDAppConfig(DAppControl.UserOperation) external => DISPATCHER(true);
    // _.getCalldataCost() external => DISPATCHER(true);
}



use builtin rule sanity filtered { f -> f.contract == currentContract  
        // && f.selector == sig:solverCall(Atlas.Context,Atlas.SolverOperation,uint256,bytes).selector 
    }

