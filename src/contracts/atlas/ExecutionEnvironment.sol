//SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.16;

import { ISearcherContract } from "../interfaces/ISearcherContract.sol";
import { ISafetyLocks } from "../interfaces/ISafetyLocks.sol";
import { IProtocolControl } from "../interfaces/IProtocolControl.sol";

import { SafeTransferLib, ERC20 } from "solmate/utils/SafeTransferLib.sol";

import {UserCall, ProtocolCall, SearcherCall, BidData, PayeeData} from "../types/CallTypes.sol";
import { CallChainProof } from "../types/VerificationTypes.sol";

import { CallVerification } from "../libraries/CallVerification.sol";
import { CallBits } from "../libraries/CallBits.sol";

import {
    ALTERED_USER_HASH,
    SEARCHER_CALL_REVERTED,
    SEARCHER_MSG_VALUE_UNPAID,
    SEARCHER_FAILED_CALLBACK,
    SEARCHER_BID_UNPAID
 } from "./Emissions.sol";

contract ExecutionEnvironment {
    using CallVerification for CallChainProof;
    using CallBits for uint16;

    address immutable public control;
    uint16 immutable public config;
    address immutable public user;
    address immutable public atlas;

    constructor(
        address _user,
        address _atlas,
        address _protocolControl,
        uint16 _callConfig
    ) {
        user = _user;
        atlas = _atlas;
        control = _protocolControl;
        config = _callConfig;
        if (!_callConfig.allowsRecycledStorage()) {
            // NOTE: selfdestruct will continue to work post EIP-6780 when it is triggered
            // in the same transaction as contract creation, which is what we do here.
            // selfdestruct(payable(_atlas));
        }
    } 

      //////////////////////////////////
     ///    CORE CALL FUNCTIONS     ///
    //////////////////////////////////
    function stagingWrapper(
        CallChainProof calldata proof,
        ProtocolCall calldata protocolCall,
        UserCall calldata userCall
    ) external returns (bytes memory stagingData) {
        // msg.sender = atlas
        // address(this) = ExecutionEnvironment
        require(msg.sender == atlas, "ERR-CE00 InvalidSenderStaging");

        bytes memory stagingCalldata = abi.encodeWithSelector(
            IProtocolControl.stageCall.selector,
            userCall.to, 
            userCall.from,
            bytes4(userCall.data), 
            userCall.data[4:]
        );

        // Verify the proof to ensure this isn't happening out of sequence.
        require(
            proof.prove(protocolCall.to, stagingCalldata),
            "ERR-P01 ProofInvalid"
        );

        bool success;

        if (protocolCall.callConfig.needsDelegateStaging()) {
            (success, stagingData) = protocolCall.to.delegatecall(
                stagingCalldata
            );
            require(success, "ERR-EC02 DelegateRevert");
        
        } else {
            (success, stagingData) = protocolCall.to.staticcall(
                stagingCalldata
            );
            require(success, "ERR-EC03 StaticRevert");
        }
    }

    function userWrapper(
        CallChainProof calldata proof,
        ProtocolCall calldata protocolCall,
        UserCall calldata userCall
    ) external payable returns (bytes memory userReturnData) {
        // msg.sender = atlas
        // address(this) = ExecutionEnvironment
        require(msg.sender == atlas, "ERR-CE00 InvalidSenderStaging");
        require(address(this).balance >= userCall.value, "ERR-CE01 ValueExceedsBalance");

        // Verify the proof to ensure this isn't happening out of sequence. 
        require(
            proof.prove(userCall.to, userCall.data),
            "ERR-P01 ProofInvalid"
        );

        bool success;

        // regular user call - executed at regular destination and not performed locally
        if (!protocolCall.callConfig.needsLocalUser()) {

            (success, userReturnData) = userCall.to.call{
                value: userCall.value
            }(
                userCall.data
            );
            require(success, "ERR-EC04a CallRevert");
        
        } else {
            if (protocolCall.callConfig.needsDelegateUser()) {
                (success, userReturnData) = protocolCall.to.delegatecall(
                    abi.encodeWithSelector(
                        IProtocolControl.userLocalCall.selector,
                        userCall.to, 
                        userCall.value,
                        userCall.data
                    )
                );
                require(success, "ERR-EC02 DelegateRevert");
            
            } else {
                revert("ERR-P02 UserCallStatic");
            }
        }

        uint256 balance = address(this).balance;
        if (balance > 0) {
            SafeTransferLib.safeTransferETH(
                msg.sender, 
                balance
            );
        }
    }

    function verificationWrapper(
        CallChainProof calldata proof,
        ProtocolCall calldata protocolCall,
        bytes memory stagingReturnData, 
        bytes memory userReturnData
    ) external {
        // msg.sender = atlas
        // address(this) = ExecutionEnvironment
        require(msg.sender == atlas, "ERR-CE00 InvalidSenderStaging");

        bytes memory data = abi.encodeWithSelector(
            IProtocolControl.verificationCall.selector, 
            stagingReturnData,
            userReturnData
        );

        // Verify the proof to ensure this isn't happening out of sequence.
        require(
            proof.prove(protocolCall.to, data),
            "ERR-P01 ProofInvalid"
        );
        if (protocolCall.callConfig.needsDelegateVerification()) {
            (bool success, bytes memory returnData) = protocolCall.to.delegatecall(
                data
            );
            require(success, "ERR-EC02 DelegateRevert");
            require(abi.decode(returnData, (bool)), "ERR-EC03 DelegateUnsuccessful");
        
        } else {
            (bool success, bytes memory returnData) = protocolCall.to.staticcall(
                data
            );
            require(success, "ERR-EC03 StaticRevert");
            require(abi.decode(returnData, (bool)), "ERR-EC03 DelegateUnsuccessful");
        }
    }


    function searcherMetaTryCatch(
        CallChainProof calldata proof,
        uint256 gasLimit,
        uint256 escrowBalance,
        SearcherCall calldata searcherCall
    ) external payable {
        // msg.sender = atlas
        // address(this) = ExecutionEnvironment
        require(msg.sender == atlas, "ERR-04 InvalidCaller");
        require(
            address(this).balance == searcherCall.metaTx.value,
            "ERR-CE05 IncorrectValue"
        );

        // Track token balances to measure if the bid amount is paid.
        uint256[] memory tokenBalances = new uint[](searcherCall.bids.length);
        uint256 i;
        for (; i < searcherCall.bids.length;) {

            // Ether balance
            if (searcherCall.bids[i].token == address(0)) {
                tokenBalances[i] = msg.value;  // NOTE: this is the meta tx value

            // ERC20 balance
            } else {
                tokenBalances[i] = ERC20(searcherCall.bids[i].token).balanceOf(address(this));
            }
            unchecked {++i;}
        }

          ////////////////////////////
         // SEARCHER SAFETY CHECKS //
        ////////////////////////////

        // Verify that the searcher's view of the user's calldata hasn't been altered
        // NOTE: Although this check may seem redundant since the user's calldata is in the
        // searcher hash chain as verified below, remember that the protocol submits the  
        // full hash chain, which user verifies. This check therefore allows the searcher
        // not to have to worry about user+protocol collaboration to exploit the searcher. 
        require(proof.userCallHash == searcherCall.metaTx.userCallHash, ALTERED_USER_HASH);

        // Verify that the searcher's calldata is unaltered and being executed in the correct order
        proof.prove(searcherCall.metaTx.from, searcherCall.metaTx.data);

        // Execute the searcher call. 
        (bool success,) = ISearcherContract(searcherCall.metaTx.to).metaFlashCall{
            gas: gasLimit, 
            value: searcherCall.metaTx.value
        }(
            searcherCall.metaTx.from,
            searcherCall.metaTx.data,
            searcherCall.bids
        );

        // Verify that it was successful
        require(success, SEARCHER_CALL_REVERTED);
        require(ISafetyLocks(atlas).confirmSafetyCallback(), SEARCHER_FAILED_CALLBACK);

        // Verify that the searcher paid what they bid
        bool etherIsBidToken;
        i = 0;
        uint256 balance;

        for (; i < searcherCall.bids.length;) {
            
            // ERC20 tokens as bid currency
            if (!(searcherCall.bids[i].token == address(0))) {
                balance = ERC20(searcherCall.bids[i].token).balanceOf(address(this));
                require(
                    balance >= tokenBalances[i] + searcherCall.bids[i].bidAmount,
                    SEARCHER_BID_UNPAID
                );
            
            // Native Gas (Ether) as bid currency
            } else {
                balance = address(this).balance;
                require(
                    balance >= searcherCall.bids[i].bidAmount, // tokenBalances[i] = 0 for ether
                    SEARCHER_BID_UNPAID 
                );

                etherIsBidToken = true;
                
                // Transfer any surplus Ether back to escrow to add to searcher's balance
                if (balance > searcherCall.bids[i].bidAmount) {
                    SafeTransferLib.safeTransferETH(
                        atlas, 
                        balance - searcherCall.bids[i].bidAmount
                    );
                }
            }
            unchecked { ++i; }
        }

        if (!etherIsBidToken) {
            uint256 currentBalance = address(this).balance;
            if (currentBalance > 0) {
                SafeTransferLib.safeTransferETH(
                    atlas, 
                    currentBalance
                );
            }
        }

        // Verify that the searcher repaid their msg.value
        require(atlas.balance >= escrowBalance, SEARCHER_MSG_VALUE_UNPAID);
    }

    function allocateRewards(
        ProtocolCall calldata protocolCall,
        BidData[] calldata bids,
        PayeeData[] calldata payeeData
    ) external {
        // msg.sender = escrow
        // address(this) = ExecutionEnvironment
        require(msg.sender == atlas, "ERR-04 InvalidCaller");

        uint256 totalEtherReward;
        uint256 payment;
        uint256 i;      

        BidData[] memory netBids = new BidData[](bids.length);

        for (; i < bids.length;) {
            payment = (bids[i].bidAmount * 5) / 100;
           
            if (bids[i].token != address(0)) {
                SafeTransferLib.safeTransfer(ERC20(bids[i].token), address(0xa71a5), payment);
                totalEtherReward = bids[i].bidAmount - payment; // NOTE: This is transferred to protocolControl as msg.value

            } else {
                SafeTransferLib.safeTransferETH(address(0xa71a5), payment);
            }

            unchecked{ 
                netBids[i].token = bids[i].token;
                netBids[i].bidAmount = bids[i].bidAmount - payment;
                ++i;
            }
        }

        if (protocolCall.callConfig.needsDelegateAllocating()) {
            (bool success,) = protocolCall.to.delegatecall(
                abi.encodeWithSelector(
                    IProtocolControl.allocatingCall.selector,
                    totalEtherReward,
                    bids,
                    payeeData
                )
            );
            require(success, "ERR-EC02 DelegateRevert");
        
        } else {
            (bool success,) = protocolCall.to.call{
                value: totalEtherReward
            }(
                abi.encodeWithSelector(
                    IProtocolControl.allocatingCall.selector,
                    totalEtherReward,
                    bids,
                    payeeData
                )
            );
            require(success, "ERR-EC04b CallRevert");
        }
    }

      ///////////////////////////////////////
     //  USER SUPPORT / ACCESS FUNCTIONS  //
    ///////////////////////////////////////
    function withdrawERC20(address token, uint256 amount) external {
        require(msg.sender == user, "ERR-EC01 NotEnvironmentOwner");

        if (ERC20(token).balanceOf(address(this)) >= amount) {
            SafeTransferLib.safeTransfer(
                ERC20(token), 
                msg.sender, 
                amount
            );

        } else {
            revert("ERR-EC02 BalanceTooLow");
        }
    }

    function factoryWithdrawERC20(address msgSender, address token, uint256 amount) external {
        require(msg.sender == atlas, "ERR-EC10 NotFactory");
        require(msgSender == user, "ERR-EC11 NotEnvironmentOwner");

        if (ERC20(token).balanceOf(address(this)) >= amount) {
            SafeTransferLib.safeTransfer(
                ERC20(token), 
                user, 
                amount
            );

        } else {
            revert("ERR-EC02 BalanceTooLow");
        }
    }

    function withdrawEther(uint256 amount) external {
        require(msg.sender == user, "ERR-EC01 NotEnvironmentOwner");

        if (address(this).balance >= amount) {
            SafeTransferLib.safeTransferETH(
                msg.sender, 
                amount
            );
            
        } else {
            revert("ERR-EC03 BalanceTooLow");
        }
    }

    function factoryWithdrawEther(address msgSender, uint256 amount) external {
        require(msg.sender == atlas, "ERR-EC10 NotFactory");
        require(msgSender == user, "ERR-EC11 NotEnvironmentOwner");

        if (address(this).balance >= amount) {
            SafeTransferLib.safeTransferETH(
                user, 
                amount
            );
            
        } else {
            revert("ERR-EC03 BalanceTooLow");
        }
    }

    function getUser() external view returns (address _user) {
        _user = user;
    }

    function getProtocolControl() external view returns (address _control) {
        _control = control;
    }

    function getEscrow() external view returns (address _escrow) {
        _escrow = atlas;
    }

    function getCallConfig() external view returns (uint16 _config) {
        _config = config;
    }

    modifier validSender(
        ProtocolCall calldata protocolCall, // supplied by frontend
        UserCall calldata userCall
    ) {
        require(userCall.from == user, "ERR-EE01 InvalidUser");
        require(protocolCall.to == control, "ERR-EE02 InvalidControl");
        require(protocolCall.callConfig == config, "ERR-EE03 InvalidConfig");
        require(msg.sender == atlas || msg.sender == user, "ERR-EE04 InvalidSender");
        //require(tx.origin == user, "ERR-EE05 InvalidOrigin"); // DISABLE FOR FORGE TESTING
        _;
    }

    receive() external payable {}

    fallback() external payable {}

}
