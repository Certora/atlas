//SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.16;

import { ICallExecution } from "../interfaces/ICallExecution.sol";

import { FastLaneErrorsEvents } from "./Emissions.sol";

import {
    CallChainProof,
    SearcherOutcome,
    SearcherCall,
    SearcherMetaTx,
    BidData,
    PayeeData,
    PaymentData,
    UserCall,
    CallConfig
} from "../libraries/DataTypes.sol";


contract SearcherWrapper is FastLaneErrorsEvents {

    function _searcherCallWrapper(
        CallChainProof memory proof,
        uint256 gasLimit,
        SearcherCall calldata searcherCall
    ) internal returns (SearcherOutcome, uint256) {
        // Called by the escrow contract, with msg.sender as the execution environment

        // Call the execution environment
        try ICallExecution(msg.sender).searcherMetaTryCatch(
            proof, gasLimit, searcherCall
        ) {
            return (SearcherOutcome.Success, 0);
        
        // TODO: implement cheaper way to do this
        } catch Error(string memory err)  {
            
            bytes32 errorSwitch = keccak256(abi.encodePacked(err));

            if (errorSwitch == _SEARCHER_BID_UNPAID) {
                return (SearcherOutcome.BidNotPaid, 0);

            } else if (errorSwitch == _SEARCHER_MSG_VALUE_UNPAID) {
                return (SearcherOutcome.CallValueTooHigh, 0);
            
            } else if (errorSwitch == _SEARCHER_CALL_REVERTED) {
                return (SearcherOutcome.CallReverted, 0);

            } else if (errorSwitch == _ALTERED_USER_HASH) {
                return (SearcherOutcome.InvalidUserHash, 0);
            
            } else if (errorSwitch == _HASH_CHAIN_BROKEN) {
                return (SearcherOutcome.InvalidSequencing, 0);

            } else {
                return (SearcherOutcome.UnknownError, 0);
            }

        } catch {
            return (SearcherOutcome.CallReverted, 0);
        }
    }
}