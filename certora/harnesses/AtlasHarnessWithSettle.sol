import {Atlas} from "../munged/contracts/atlas/Atlas.sol";

import "../munged/contracts/types/LockTypes.sol"; 
contract AtlasHarnessWithSettle is Atlas {
        constructor(
        uint256 escrowDuration,
        uint256 atlasSurchargeRate,
        uint256 bundlerSurchargeRate,
        address verification,
        address simulator,
        address initialSurchargeRecipient,
        address l2GasCalculator,
        address factoryLib
    )
        Atlas(
            escrowDuration,
            atlasSurchargeRate,
            bundlerSurchargeRate,
            verification,
            simulator,
            initialSurchargeRecipient,
            l2GasCalculator, 
            factoryLib
        )
    { }


    function getLockEnv() external returns (address activeEnv){
        (activeEnv, , )  = _lock();
    }
    
    function getLockCallConfig() external returns (uint32 callConfig){
        ( , callConfig, ) = _lock();
    }
    
    function getLockPhase() external returns (uint8 phase){
        ( , , phase) = _lock();
    }

 
    function settle(Context memory ctx, uint256 solverGasLimit,
        address gasRefundBeneficiary) external returns (uint256, uint256) {
        return _settle(ctx, solverGasLimit, gasRefundBeneficiary);
    }
}