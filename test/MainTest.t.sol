// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

import { SafeTransferLib, ERC20 } from "solmate/utils/SafeTransferLib.sol";

import {IEscrow} from "../src/contracts/interfaces/IEscrow.sol";
import {IAtlas} from "../src/contracts/interfaces/IAtlas.sol";
import {IProtocolIntegration} from "../src/contracts/interfaces/IProtocolIntegration.sol";

import {Atlas} from "../src/contracts/atlas/Atlas.sol";
import {Mimic} from "../src/contracts/atlas/Mimic.sol";

import {V2ProtocolControl} from "../src/contracts/v2-example/V2ProtocolControl.sol";

import {Searcher} from "./searcher/src/TestSearcher.sol";

import "../src/contracts/types/CallTypes.sol";
import "../src/contracts/types/EscrowTypes.sol";
import "../src/contracts/types/LockTypes.sol";
import "../src/contracts/types/VerificationTypes.sol";

import {BaseTest} from "./base/BaseTest.t.sol";
import {Helper} from "./Helpers.sol";

import "forge-std/Test.sol";

contract MainTest is BaseTest {
    /// forge-config: default.gas_price = 15000000000
    function setUp() public virtual override {
        BaseTest.setUp();
    }

    function testMain() public {
        
        vm.label(userEOA, "USER");
        vm.label(escrow, "ESCROW");
        vm.label(address(atlas), "ATLAS");
        vm.label(address(control), "PCONTROL");
        
        ProtocolCall memory protocolCall = helper.getProtocolCall();
        
        UserCall memory userCall = helper.buildUserCall(POOL_ONE, userEOA, TOKEN_ONE);
        
        PayeeData[] memory payeeData = helper.getPayeeData();

        SearcherCall[] memory searcherCalls = new SearcherCall[](2);

        searcherCalls[0] = helper.buildSearcherCall(
            userCall, searcherOneEOA, address(searcherOne), POOL_ONE, POOL_TWO, 2E17
        );
        searcherCalls[1] = helper.buildSearcherCall(
            userCall, searcherTwoEOA, address(searcherTwo), POOL_TWO, POOL_ONE, 1E17
        );
        
        Verification memory verification = helper.buildVerification(
            governanceEOA,
            protocolCall,
            userCall,
            payeeData,
            searcherCalls
        );

        vm.startPrank(userEOA);

        address executionEnvironment = IAtlas(address(atlas)).getExecutionEnvironment(userEOA, address(control));
        vm.label(address(executionEnvironment), "ENVIRONMENT");

        console.log("userEOA",userEOA);
        console.log("atlas", address(atlas));
        console.log("control", address(control));
        console.log("executionEnvironment",executionEnvironment);

        // User must approve the execution environment
        ERC20(TOKEN_ZERO).approve(executionEnvironment, type(uint256).max);
        ERC20(TOKEN_ONE).approve(executionEnvironment, type(uint256).max);

        (bool success,) = address(atlas).call(
            abi.encodeWithSelector(
                atlas.metacall.selector, 
                protocolCall,
                userCall,
                payeeData,
                searcherCalls,
                verification
            )
        );

        assertTrue(success);
    }

    /*
    function testMimic() public {
        address aaaaa = address(this);
        address bbbbb = msg.sender;
        address ccccc = address(this);
        uint16 ddddd = uint16(0x1111);
        // Mimic mimic = new Mimic();
        //console.log("----");
        //console.log("runtime code:");
        //console.logBytes(address(mimic).code);
        console.log("aaaaa", aaaaa);
        console.log("bbbbb", bbbbb);
        console.log("ccccc", ccccc);
        console.log("----");
        console.log("creation code:");
        console.logBytes(type(Mimic).creationCode);
        console.log("----");

        bytes memory creationCode = type(Mimic).creationCode;
        //bytes memory creationCode = new bytes(790);
        assembly {
            mstore(add(creationCode, 85), add(
                shl(96, aaaaa), 
                0x73ffffffffffffffffffffff
            ))
            mstore(add(creationCode, 131), add(
                shl(96, bbbbb), 
                0x73ffffffffffffffffffffff
            ))
            mstore(add(creationCode, 152), add(
                shl(96, ccccc), 
                add(
                    add(
                        shl(88, 0x61), 
                        shl(72, ddddd)
                    ),
                    0x604051602001610082
                )
            ))
        }
        
        console.log("assembly modified code:");
        console.logBytes(creationCode);
        console.log("----");
    }
    */
}