import {Atlas} from "../munged/contracts/atlas/Atlas.sol";
import "../munged/contracts/types/UserOperation.sol";
import { IExecutionEnvironment } from "../munged/contracts/interfaces/IExecutionEnvironment.sol";
contract AtlasHarness is Atlas {
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
        phase = _phase();
    }

    function getActiveEnvironment() public returns (address activeEnv){
        activeEnv = _activeEnvironment();
    }

    function borrowHarness(uint256 amount) internal returns (bool valid){
        return _borrow(amount);
    }
    function userWrapperHarness(UserOperation calldata userOp) external{
        
        // borrow
        borrowHarness(userOp.value);

        // userWrapper
        IExecutionEnvironment(getActiveEnvironment()).userWrapper{ value: userOp.value}(userOp);
    }
    
    
    // function borrowReconcileCallback(uint256 amount, uint256 maxApprovedGasSpend) external {
    //     borrow(amount);
    //     reconcile(maxApprovedGasSpend);
    // }
}