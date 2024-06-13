//SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.22;

import { SafeTransferLib, ERC20 } from "solmate/utils/SafeTransferLib.sol";
import { Base } from "src/contracts/common/ExecutionBase.sol";

import { ISolverContract } from "src/contracts/interfaces/ISolverContract.sol";
import { ISafetyLocks } from "src/contracts/interfaces/ISafetyLocks.sol";
import { IDAppControl } from "src/contracts/interfaces/IDAppControl.sol";
import { IEscrow } from "src/contracts/interfaces/IEscrow.sol";

import { AtlasErrors } from "src/contracts/types/AtlasErrors.sol";
import { CallBits } from "src/contracts/libraries/CallBits.sol";
import { ExecutionPhase } from "src/contracts/types/LockTypes.sol";
import "src/contracts/types/SolverCallTypes.sol";
import "src/contracts/types/UserCallTypes.sol";
import "src/contracts/types/DAppApprovalTypes.sol";

/// @title ExecutionEnvironment
/// @author FastLane Labs
/// @notice An Execution Environment contract is deployed for each unique combination of User address x DAppControl
/// address that interacts with the Atlas protocol via a metacall transaction.
contract ExecutionEnvironment is Base {
    using CallBits for uint32;

    uint8 private constant _ENVIRONMENT_DEPTH = 1 << 1;

    constructor(address _atlas) Base(_atlas) { }

    modifier validUser(UserOperation calldata userOp) {
        if (userOp.to != ATLAS || userOp.dapp == ATLAS) revert AtlasErrors.InvalidTo();
        _;
    }

    //////////////////////////////////
    ///    CORE CALL FUNCTIONS     ///
    //////////////////////////////////

    /// @notice The preOpsWrapper function may be called by Atlas before the UserOperation is executed.
    /// @dev This contract is called by the Atlas contract, and delegatecalls the DAppControl contract via the
    /// corresponding `preOpsCall` function.
    /// @param userOp The UserOperation struct.
    /// @return preOpsData Data to be passed to the next call phase.
    function preOpsWrapper(UserOperation calldata userOp)
        external
        validUser(userOp)
        onlyAtlasEnvironment(ExecutionPhase.PreOps, _ENVIRONMENT_DEPTH)
        returns (bytes memory)
    {
        bytes memory preOpsData = _forward(abi.encodeCall(IDAppControl.preOpsCall, userOp));

        bool success;
        (success, preOpsData) = _control().delegatecall(preOpsData);

        if (!success) revert AtlasErrors.PreOpsDelegatecallFail();

        preOpsData = abi.decode(preOpsData, (bytes));
        return preOpsData;
    }

    /// @notice The userWrapper function is called by Atlas to execute the UserOperation.
    /// @dev This contract is called by the Atlas contract, and either delegatecalls or calls the DAppControl contract
    /// with `userOp.data` as calldata, depending on the the needsDelegateUser flag.
    /// @param userOp The UserOperation struct.
    /// @return returnData Data to be passed to the next call phase.
    function userWrapper(UserOperation calldata userOp)
        external
        payable
        validUser(userOp)
        onlyAtlasEnvironment(ExecutionPhase.UserOperation, _ENVIRONMENT_DEPTH)
        returns (bytes memory returnData)
    {
        uint32 config = _config();

        if (userOp.value > address(this).balance) revert AtlasErrors.UserOpValueExceedsBalance();

        // Do not attach extra calldata via `_forward()` if contract called is not dAppControl, as the additional
        // calldata may cause unexpected behaviour in third-party protocols
        bytes memory callData = (userOp.dapp != userOp.control) ? userOp.data : _forward(userOp.data);
        bool success;

        if (config.needsDelegateUser()) {
            (success, returnData) = userOp.dapp.delegatecall(callData);
            if (!success) revert AtlasErrors.UserWrapperDelegatecallFail();
        } else {
            // regular user call - executed at regular destination and not performed locally
            (success, returnData) = userOp.dapp.call{ value: userOp.value }(callData);
            if (!success) revert AtlasErrors.UserWrapperCallFail();
        }
    }

    /// @notice The postOpsWrapper function may be called by Atlas as the last phase of a `metacall` transaction.
    /// @dev This contract is called by the Atlas contract, and delegatecalls the DAppControl contract via the
    /// corresponding `postOpsCall` function.
    /// @param solved Boolean indicating whether a winning SolverOperation was executed successfully.
    /// @param returnData Data returned from the previous call phase.
    function postOpsWrapper(
        bool solved,
        bytes calldata returnData
    )
        external
        onlyAtlasEnvironment(ExecutionPhase.PostOps, _ENVIRONMENT_DEPTH)
    {
        bytes memory data = _forward(abi.encodeCall(IDAppControl.postOpsCall, (solved, returnData)));

        bool success;
        (success, data) = _control().delegatecall(data);

        if (!success) revert AtlasErrors.PostOpsDelegatecallFail();
        if (!abi.decode(data, (bool))) revert AtlasErrors.PostOpsDelegatecallReturnedFalse();
    }

    /// @notice The solverPreTryCatch function is called by Atlas to execute the preSolverCall part of each SolverOperation. A SolverTracker struct is also returned, containing bid info needed to handle the difference in logic between inverted and non-inverted bids.
    /// @param bidAmount The Solver's bid amount.
    /// @param solverOp The SolverOperation struct.
    /// @param returnData Data returned from the previous call phase.
    /// @return solverTracker Bid tracking information for the current solver.
    function solverPreTryCatch(
        uint256 bidAmount,
        SolverOperation calldata solverOp,
        bytes calldata returnData
    )
        external
        payable
        onlyAtlasEnvironment(ExecutionPhase.PreSolver, _ENVIRONMENT_DEPTH)
        returns (SolverTracker memory solverTracker)
    {
        // Verify that the DAppControl contract matches the solver's expectations
        if (solverOp.control != _control()) {
            revert AtlasErrors.AlteredControl();
        }

        solverTracker.bidAmount = bidAmount;
        solverTracker.etherIsBidToken = solverOp.bidToken == address(0);

        // bidValue is inverted; Lower bids are better; solver must withdraw <= bidAmount
        if (_config().invertsBidValue()) {
            solverTracker.invertsBidValue = true;
            // if invertsBidValue, record ceiling now
            // inventory to send to solver must have been transferred in by userOp or preOp call
            solverTracker.ceiling = solverTracker.etherIsBidToken
                ? address(this).balance
                : ERC20(solverOp.bidToken).balanceOf(address(this));
        }

        // Handle any solver preOps, if necessary
        if (_config().needsPreSolver()) {
            bool success;
            bytes memory data = _forward(abi.encodeCall(IDAppControl.preSolverCall, (solverOp, returnData)));

            (success, data) = _control().delegatecall(data);

            if (!success || !abi.decode(data, (bool))) {
                revert AtlasErrors.PreSolverFailed();
            }
        }

        // bidValue is not inverted; Higher bids are better; solver must deposit >= bidAmount
        if (!solverTracker.invertsBidValue) {
            // if invertsBidValue, record floor now
            solverTracker.floor = solverTracker.etherIsBidToken
                ? address(this).balance
                : ERC20(solverOp.bidToken).balanceOf(address(this));
        }
    }

    /// @notice The solverPostTryCatch function is called by Atlas to execute the postSolverCall part of each SolverOperation. The different logic scenarios depending on the value of invertsBidValue are also handled, and the SolverTracker struct is updated accordingly.
    /// @param solverOp The SolverOperation struct.
    /// @param returnData Data returned from the previous call phase.
    /// @param solverTracker Bid tracking information for the current solver.
    /// @return solverTracker Updated bid tracking information for the current solver.
    function solverPostTryCatch(
        SolverOperation calldata solverOp,
        bytes calldata returnData,
        SolverTracker memory solverTracker
    )
        external
        payable
        onlyAtlasEnvironment(ExecutionPhase.PostSolver, _ENVIRONMENT_DEPTH)
        returns (SolverTracker memory)
    {
        // bidValue is inverted; Lower bids are better; solver must withdraw <= bidAmount
        if (solverTracker.invertsBidValue) {
            // if invertsBidValue, record floor now
            solverTracker.floor = solverTracker.etherIsBidToken
                ? address(this).balance
                : ERC20(solverOp.bidToken).balanceOf(address(this));
        }

        bool success;
        if (_config().needsSolverPostCall()) {
            bytes memory data = _forward(abi.encodeCall(IDAppControl.postSolverCall, (solverOp, returnData)));

            (success, data) = _control().delegatecall(data);

            if (!success) {
                revert AtlasErrors.PostSolverFailed();
            }

            if (!abi.decode(data, (bool))) {
                revert AtlasErrors.IntentUnfulfilled();
            }
        }

        // bidValue is not inverted; Higher bids are better; solver must deposit >= bidAmount
        if (!solverTracker.invertsBidValue) {
            // if not invertsBidValue, record ceiling now
            solverTracker.ceiling = solverTracker.etherIsBidToken
                ? address(this).balance
                : ERC20(solverOp.bidToken).balanceOf(address(this));
        }

        // Make sure the numbers add up and that the bid was paid
        if (solverTracker.floor > solverTracker.ceiling) revert AtlasErrors.SolverBidUnpaid();

        uint256 netBid = solverTracker.ceiling - solverTracker.floor;

        // If bids aren't inverted, revert if net amount received is less than the bid
        if (!solverTracker.invertsBidValue && netBid < solverTracker.bidAmount) revert AtlasErrors.SolverBidUnpaid();

        // If bids are inverted, revert if the net amount sent is more than the bid
        if (solverTracker.invertsBidValue && netBid > solverTracker.bidAmount) revert AtlasErrors.SolverBidUnpaid();

        // Update the bidAmount to the bid received
        solverTracker.bidAmount = netBid;

        return solverTracker;
    }

    /// @notice The allocateValue function is called by Atlas after a successful SolverOperation.
    /// @dev This contract is called by the Atlas contract, and delegatecalls the DAppControl contract via the
    /// corresponding `allocateValueCall` function.
    /// @param bidToken The address of the token used for the winning SolverOperation's bid.
    /// @param bidAmount The winning bid amount.
    /// @param allocateData Data returned from the previous call phase.
    function allocateValue(
        address bidToken,
        uint256 bidAmount,
        bytes memory allocateData
    )
        external
        onlyAtlasEnvironment(ExecutionPhase.HandlingPayments, _ENVIRONMENT_DEPTH)
    {
        allocateData = _forward(abi.encodeCall(IDAppControl.allocateValueCall, (bidToken, bidAmount, allocateData)));

        (bool success,) = _control().delegatecall(allocateData);
        if (!success) revert AtlasErrors.AllocateValueDelegatecallFail();

        uint256 balance = address(this).balance;
        if (balance > 0) {
            IEscrow(ATLAS).contribute{ value: balance }();
        }
    }

    ///////////////////////////////////////
    //  USER SUPPORT / ACCESS FUNCTIONS  //
    ///////////////////////////////////////

    /// @notice The withdrawERC20 function allows the environment owner to withdraw ERC20 tokens from this Execution
    /// Environment.
    /// @dev This function is only callable by the environment owner and only when Atlas is in an unlocked state.
    /// @param token The address of the ERC20 token to withdraw.
    /// @param amount The amount of the ERC20 token to withdraw.
    function withdrawERC20(address token, uint256 amount) external {
        if (msg.sender != _user()) revert AtlasErrors.NotEnvironmentOwner();
        if (!ISafetyLocks(ATLAS).isUnlocked()) revert AtlasErrors.AtlasLockActive();

        if (ERC20(token).balanceOf(address(this)) >= amount) {
            SafeTransferLib.safeTransfer(ERC20(token), msg.sender, amount);
        } else {
            revert AtlasErrors.ExecutionEnvironmentBalanceTooLow();
        }
    }

    /// @notice The withdrawEther function allows the environment owner to withdraw Ether from this Execution
    /// Environment.
    /// @dev This function is only callable by the environment owner and only when Atlas is in an unlocked state.
    /// @param amount The amount of Ether to withdraw.
    function withdrawEther(uint256 amount) external {
        if (msg.sender != _user()) revert AtlasErrors.NotEnvironmentOwner();
        if (!ISafetyLocks(ATLAS).isUnlocked()) revert AtlasErrors.AtlasLockActive();

        if (address(this).balance >= amount) {
            SafeTransferLib.safeTransferETH(msg.sender, amount);
        } else {
            revert AtlasErrors.ExecutionEnvironmentBalanceTooLow();
        }
    }

    /// @notice The getUser function returns the address of the user of this Execution Environment.
    /// @return user The address of the user of this Execution Environment.
    function getUser() external pure returns (address user) {
        user = _user();
    }

    /// @notice The getControl function returns the address of the DAppControl contract of the current metacall
    /// transaction.
    /// @return control The address of the DAppControl contract of the current metacall transaction.
    function getControl() external pure returns (address control) {
        control = _control();
    }

    /// @notice The getConfig function returns the CallConfig of the current metacall transaction.
    /// @return config The CallConfig in uint32 form of the current metacall transaction.
    function getConfig() external pure returns (uint32 config) {
        config = _config();
    }

    /// @notice The getEscrow function returns the address of the Atlas/Escrow contract.
    /// @return The address of the Atlas/Escrow contract.
    function getEscrow() external view returns (address) {
        return ATLAS;
    }

    receive() external payable { }

    fallback() external payable { }
}
