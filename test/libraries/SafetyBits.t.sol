// SPDX-License-Identifier: MIT
pragma solidity 0.8.22;

import "forge-std/Test.sol";

import { SafetyBits } from "src/contracts/libraries/SafetyBits.sol";
import "src/contracts/types/LockTypes.sol";
import "../base/TestUtils.sol";

import { CallBits } from "src/contracts/libraries/CallBits.sol";

import { CallConfigIndex } from "src/contracts/types/DAppApprovalTypes.sol";

contract SafetyBitsTest is Test {
    using SafetyBits for Context;
    using CallBits for uint32;

    function initializeContext(CallConfigIndex index) public view returns (Context memory ctx) {
        uint32 callConfig = uint32(1 << uint256(index));
        ctx = _buildContext(callConfig, address(0), bytes32(0), address(0), 1, false);
    }

    function _getCallConfig(CallConfigIndex index) internal pure returns (uint32 callConfig) {
        callConfig = uint32(1 << uint256(index));
    }

    function _buildContext(
        uint32 callConfig,
        address executionEnvironment,
        bytes32 userOpHash,
        address bundler,
        uint8 solverOpCount,
        bool isSimulation
    )
        internal
        view
        returns (Context memory)
    {   
        return Context({
            executionEnvironment: executionEnvironment,
            userOpHash: userOpHash,
            bundler: bundler,
            solverSuccessful: false,
            paymentsSuccessful: false,
            callIndex: callConfig.needsPreOpsCall() ? 0 : 1,
            callCount: solverOpCount + 3,
            phase: uint8(ExecutionPhase.Uninitialized),
            solverOutcome: 0,
            bidFind: false,
            isSimulation: isSimulation,
            callDepth: 0
        });
    }

    function testInitializeEscrowLock() public {
        Context memory ctx = initializeContext(CallConfigIndex.RequirePreOps);
        assertTrue(ctx.solverSuccessful == false);
        assertTrue(ctx.paymentsSuccessful == false);
        assertTrue(ctx.callIndex == 0);
        assertTrue(ctx.callCount == 4);
        assertTrue(ctx.phase == uint8(ExecutionPhase.Uninitialized));
        assertTrue(ctx.solverOutcome == 0);
    }
}
