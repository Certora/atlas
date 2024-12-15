import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";

use builtin rule sanity filtered { f -> f.contract == currentContract 
    // && f.selector == sig:metacallSimulation(
    //     (address,address,uint256,uint256,uint256,uint256,uint256,address,address,uint32,address,bytes,bytes),
    //     (address,address,uint256,uint256,uint256,uint256,address,address,bytes32,address,uint256,bytes,bytes)[],
    //     (address,address,uint256,uint256,address,address,bytes32,bytes32,bytes)
    // ).selector 
    && f.selector != sig:metacallSimulation(Simulator.UserOperation, Simulator.SolverOperation[], Simulator.DAppOperation).selector
    }


