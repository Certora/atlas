import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";


methods {
    // function _.getL1FeeUpperBound(uint256) external => DISPATCHER(true); // there is no implementation
}


use builtin rule sanity filtered { f -> f.contract == currentContract }
