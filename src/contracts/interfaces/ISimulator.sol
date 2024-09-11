//SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.25;

import "src/contracts/types/SolverOperation.sol";
import "src/contracts/types/UserOperation.sol";
import "src/contracts/types/ConfigTypes.sol";
import "src/contracts/types/DAppOperation.sol";

enum Result {
    Unknown,
    VerificationSimFail,
    PreOpsSimFail,
    UserOpSimFail,
    SolverSimFail,
    AllocateValueSimFail,
    PostOpsSimFail,
    SimulationPassed
}

interface ISimulator {
    function simUserOperation(UserOperation calldata userOp)
        external
        payable
        returns (bool success, Result simResult, uint256);

    function simSolverCall(
        UserOperation calldata userOp,
        SolverOperation calldata solverOp,
        DAppOperation calldata verification
    )
        external
        payable
        returns (bool success, Result simResult, uint256);

    function simSolverCalls(
        UserOperation calldata userOp,
        SolverOperation[] calldata solverOps,
        DAppOperation calldata verification
    )
        external
        payable
        returns (bool success, Result simResult, uint256);
}
