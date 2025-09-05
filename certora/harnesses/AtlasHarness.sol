import {Atlas} from "../../src/contracts/atlas/Atlas.sol";
import "../../src/contracts/types/UserOperation.sol";
import { IExecutionEnvironment } from "../../src/contracts/interfaces/IExecutionEnvironment.sol";
import { GasAccLib } from "../../src/contracts/libraries/GasAccLib.sol";
import { AccountingMath } from "../../src/contracts/libraries/AccountingMath.sol";


contract AtlasHarness is Atlas {
    using GasAccLib for uint256;
    using AccountingMath for uint256;

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


    function getLockEnv() external view returns (address activeEnv){
        (activeEnv, , )  = _lock();
    }
    
    function getLockCallConfig() external view returns (uint32 callConfig){
        ( , callConfig, ) = _lock();
    }
    
    function getLockPhase() external view returns (uint8 phase){
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

    function getBorrowLedgerBorrows() external view returns (uint128) {
        return t_borrowsLedger.toBorrowsLedger().borrows;
    }
    function getBorrowLedgerRepays() external view returns (uint128) {
        return t_borrowsLedger.toBorrowsLedger().repays;
    }    
    
    
    // function borrowReconcileCallback(uint256 amount, uint256 maxApprovedGasSpend) external {
    //     borrow(amount);
    //     reconcile(maxApprovedGasSpend);
    // }

    function havocAll() external {
        this.havocAll();
    }

    function computeGasFees(uint256 gasPrice) external view returns (uint256) {
        (uint256 _atlasSurchargeRate, uint256 _bundlerSurchargeRate) = _surchargeRates();
        return uint256(t_gasLedger.toGasLedger().solverFaultFailureGas).withSurcharge(_atlasSurchargeRate + _bundlerSurchargeRate) * gasPrice;
    }

}
