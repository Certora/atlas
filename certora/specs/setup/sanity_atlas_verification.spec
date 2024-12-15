import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";


methods{ 
    function _.CALL_CONFIG() external => DISPATCHER(true);
    function _.getDAppSignatory() external => DISPATCHER(true);
    // _.getCalldataCost() external => DISPATCHER(true);
}



use builtin rule sanity filtered { f -> f.contract == currentContract  
        // && f.selector == sig:solverCall(Atlas.Context,Atlas.SolverOperation,uint256,bytes).selector 
    }

