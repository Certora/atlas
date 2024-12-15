import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";


methods{ 
    function _.CALL_CONFIG() external => DISPATCHER(true);
    function _.getDAppSignatory() external => DISPATCHER(true);
}



use builtin rule sanity filtered { f -> f.contract == currentContract  
    }

