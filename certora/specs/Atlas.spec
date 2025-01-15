import "./ERC20/erc20cvl.spec";
// import "./MathSummaries.spec";
using AtlasVerification as AtlasVerification;

methods{ 
    function _.CALL_CONFIG() external => DISPATCHER(true);

    function _.getDAppConfig(Atlas.UserOperation) external => NONDET;
    function _.initialGasUsed(uint256) external => NONDET;
    function _._computeSalt(address, address, uint32) internal => NONDET;
    function CallBits.exPostBids(uint32) internal returns bool => ALWAYS(false);
    function AtlasVerification.verifySolverOp(Atlas.SolverOperation, bytes32 ,uint256, address, bool) external returns uint256 => NONDET; // xxx
    function Escrow._checkSolverBidToken(address, address, uint256) internal returns uint256 => NONDET;
    function Escrow._validateSolverOpDeadline(Atlas.SolverOperation calldata, Atlas.DAppConfig memory) internal returns uint256 => NONDET;
    function Escrow._checkTrustedOpHash(Atlas.DAppConfig memory, bool, Atlas.UserOperation calldata, Atlas.SolverOperation calldata, uint256) internal returns uint256 => NONDET;
    function GasAccounting._updateAnalytics(Atlas.EscrowAccountAccessData memory, bool, uint256) internal => NONDET;
    function Factory._getOrCreateExecutionEnvironment(address, address, uint32) internal returns address => NONDET;
    function _.getCalldataCost(uint256) external => CONSTANT;
    
    // getters
    function getLockEnv() external returns address envfree;
    function getLockCallConfig() external returns uint32 envfree;
    function getLockPhase() external returns uint8 envfree;
    function Escrow._solverOpWrapper(Atlas.Context memory, Atlas.SolverOperation calldata, uint256, uint256, bytes memory) internal returns (uint256, Atlas.SolverTracker memory) => borrowReconcileCVL(); // xxx
    
    // checking if this avoids the failed to locate function error
    // function _._allocateValueCall(address, uint256, bytes calldata) internal => NONDET;
    // function _._getCallConfig(uint32) internal => NONDET;

    // function _._getMimicCreationCode(address, address, uint32) internal => CONSTANT;
    
    // unresolved external in _._ => DISPATCH [
    //     // ExecutionEnvironment.preOpsWrapper(Atlas.UserOperation)
    //     ExecutionEnvironment.postOpsWrapper(bool, bytes),
        

    // ] default HAVOC_ALL;

    // _.getCalldataCost() external => DISPATCHER(true);
    
    // unresolved external in _._ => DISPATCH [
    //     // FactoryLib.getOrCreateExecutionEnvironment(address, address, uint32, bytes32),
    //     // AtlasVerification.validateCalls(Atlas.DAppConfig, Atlas.UserOperation, 
    //                                     // Atlas.SolverOperation[], Atlas.DAppOperation, uint256, address, bool),
    //     // Atlas.execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool),
    //     // ExecutionEnvironment.solverPreTryCatch(uint256, Atlas.SolverOperation, bytes),
    //     // SolverBase.atlasSolverCall(address, address, address, uint256, bytes, bytes),
    //     FastLaneOnlineControl.postOpsCall(bool, bytes)
    // ] default HAVOC_ALL;
    // function _._executeUserOperation(Atlas.Context memory, Atlas.DAppConfig memory, Atlas.UserOperation calldata, bytes memory) internal  => NONDET;
    // function Escrow._executeUserOperation(Atlas.Context memory, Atlas.DAppConfig memory, Atlas.UserOperation calldata, bytes memory) internal returns bytes memory => _executeUserOperationCVL;
}
/*----------------------------------------------------------------------------------------------------------------
                                                 GHOSTS & HOOKS 
----------------------------------------------------------------------------------------------------------------*/


// ghost tracking the sum of atlETH bonded balances
persistent ghost mathint sumOfBonded{
    init_state axiom sumOfBonded == 0;
}
// ghost tracking the sum of atlETH unbonded balances
persistent ghost mathint sumOfUnbonded{
    init_state axiom sumOfUnbonded == 0;
}
// ghost tracking the sum of atlETH unbonding balances
persistent ghost mathint sumOfUnbonding{
    init_state axiom sumOfUnbonding == 0;
}

// ghost bytes[8] _executeUserOperationCVL;

// ghost tracking the transient variable t_withdrawals
ghost uint256 withdrawals{
    init_state axiom withdrawals == 0;
}
// ghost tracking the transient variable t_deposits
ghost uint256 deposits{
    init_state axiom deposits == 0;
}

// Hooks for bonded balances
hook Sstore S_accessData[KEY address a].bonded uint112 new_value (uint112 old_value) {
    sumOfBonded = sumOfBonded - old_value + new_value;
}
hook Sload uint112 value S_accessData[KEY address a].bonded {
     require value <= sumOfBonded;
}


// SSTORE hook for unbonded balances
hook Sstore s_balanceOf[KEY address a].balance uint112 new_value (uint112 old_value) {
    sumOfUnbonded = sumOfUnbonded - old_value + new_value;
}

hook Sload uint112 value s_balanceOf[KEY address a].balance {
     require value <= sumOfUnbonded;
}


// SSTORE hook for unbonding balances
hook Sstore s_balanceOf[KEY address a].unbonding uint112 new_value (uint112 old_value) {
    sumOfUnbonding = sumOfUnbonding - old_value + new_value;
}

hook Sload uint112 value s_balanceOf[KEY address a].unbonding {
     require value <= sumOfUnbonding;
}

// update ghost withdrawals and deposits
hook ALL_TSTORE(uint256 loc, uint256 v) {
    if (loc == 7) 
        withdrawals = v;
    if (loc == 8) 
        deposits = v; 
}

hook ALL_TLOAD(uint loc) uint v {
    if (loc == 7) 
        require withdrawals == v; 
    if (loc == 8) 
        require deposits == v; 
}

/*----------------------------------------------------------------------------------------------------------------
                                                 CVL FUNCTIONS
----------------------------------------------------------------------------------------------------------------*/

function borrowReconcileCVL() returns (uint256, Atlas.SolverTracker){
    env e;
    uint256 amount;
    borrow(e, amount);

    uint256 maxApprovedGasSpend;
    reconcile(e, maxApprovedGasSpend);

    uint256 result;
    Atlas.SolverTracker solverTracker;

    return (result, solverTracker);
}



/*----------------------------------------------------------------------------------------------------------------
                                                 RULE & INVARIANTS 
----------------------------------------------------------------------------------------------------------------*/

// Atlas ETH balance = sum of AtlETH accounts {unbonded + bonded + unbonding} + cumulativeSurcharge
// STATUS: WIP
// https://prover.certora.com/output/11775/491f675db3684c879139e5cb3eec1978?anonymousKey=df546cdf06061b631db3aa93dc714077761f37e6 - first run
// https://prover.certora.com/output/11775/ee77ef4812704c34a1e9fe4d2e9e8efe?anonymousKey=1cd822d3bc74b882addb7596bdc06bc432a8b471 - wtih preserved block eth balance before == 0
// https://prover.certora.com/output/11775/e04429d738a44ca1a503de782079286e?anonymousKey=a6561d3da5c5c61858b24e289866600abdc2d534 - with init state 0 for ghosts
// https://prover.certora.com/output/11775/d4675c7e440f4d439bdd3fdece968828?anonymousKey=336c990744233c71d88fbe9fb4c191c2b8bf7a88 - with dispatch list for delegate call
// https://prover.certora.com/output/11775/008f73e296dc457999655acbc20f371c?anonymousKey=1b17761e93fba8e78a79d421be79f3eec3830ee0 - _._ DISPATCH_LIST - lot of timeouts including metacall
// https://prover.certora.com/output/11775/f26379578d264020bfde4fb1f7da9011?anonymousKey=a099fb18c50c962bf4156bbd9a3609b78f296031 - with parametric contracts Atlas - - lot of timeouts including metacall
// https://prover.certora.com/output/11775/4797f493fd994a4a89b82f9117c1c8aa?anonymousKey=c8b7490e914d3aa19b6db3523806fb82addebc01 - with metacall try catch block munging
// https://prover.certora.com/output/11775/e300cf8310af4e66a95079e1798935c0?anonymousKey=8d7487c88cc203e07aa8a084a722898a65751ba9 - above but munging also comments out _settle

// ///////////// latest code //////////////////
// https://prover.certora.com/output/11775/04ee3c350db24bac90167e57b091a505?anonymousKey=c97d301955fc7b27a3e45d54d74f7ff52fc321fb - without muning in try catch
// https://prover.certora.com/output/11775/f24f7f731e9847c8afd0b9f3c6d4daa6?anonymousKey=55076cafea073044c281fd275696d1b22f95136f - with munging in try catch (includes _settle call)
// https://prover.certora.com/output/11775/1440111df25344688fb5687ab0130f5c?anonymousKey=b796bef30b21889c14821d111538735d8a3aa6d8 - with john's branch
// https://prover.certora.com/output/11775/dae7a94d438548ae8946d78cc7ab9934?anonymousKey=46fcf8be00fac97747f1fce9d33af8ed6ca9f1b3 - with validateCalls NONDET
// https://prover.certora.com/output/11775/c349c6e7a61449938e83b65365af2cc7?anonymousKey=a9777b73e713cbe2ead70dfd34e9c6d83bb291b5 - with executeUserOperation NONDET
// https://prover.certora.com/output/11775/26afc40cdeda4dacba8e92cdc4574862?anonymousKey=b377044c9e30d9b36b2d9b7843385178eeb99e43 - with _allocateValueCal NONDET
// https://prover.certora.com/output/11775/5fbf52164faf4de3902d6909fb556131?anonymousKey=4968c5c91b21c0603769f473f4954d3d6a065704 - with getCallConfig NONDET
// https://prover.certora.com/output/11775/c485bc32dd884ef39d123a3f7e4e27ed?anonymousKey=2793cca00334424b7d5ed0c9e5629fc7ac681619 - with safeTransferLib ERC20 NONDET
// https://prover.certora.com/output/11775/dff3f7065b6a4056a674a9412248a47e?anonymousKey=ae56c54d46e119840464a432be0d5610501a0d79 - wtih call to executeUserOperation commented out in metacall
// https://prover.certora.com/output/11775/32690964461f4c89a89d6e175caca5e5?anonymousKey=05cbafb99e612ce27ad5f2de9a62751e6960a2f9 - with validateCalls body commented out
// https://prover.certora.com/output/11775/c3e7705f4106466d9f076fd4b77e832d?anonymousKey=4d8d9498a17594c4b648d0546b9773bf2d01b984 - with exPostBids, _bidFindingIteration and _bidKnownIteration NONDET
// https://prover.certora.com/output/11775/96f0d5dc0f6c4b24bdf00255954ea46c?anonymousKey=11fde063bf930fb443727f026819595c0bd26cca - with postOpsCall in dispatch list
// https://prover.certora.com/output/11775/21b72adca41043f085e9d92ecbd64dda?anonymousKey=03c8df6d26af769225995403809c345e48a918cd - without preserved block
// https://prover.certora.com/output/11775/b60dce56ef0443cbb909c9511ff11452?anonymousKey=37e4d6103e92ea6c1ade7169b39485b096475c42 - with depth 0 and exPostBids false
// https://prover.certora.com/output/11775/d51bc1b97955462eaccd8a88d1bfe0e9?anonymousKey=86c6b19ccbcff109df106e0613dfc7404a50ad29 - with depth 0 and both paths with exPostBids
// https://prover.certora.com/output/11775/2e097a5f82e347989a9a9f968ff35ccb?anonymousKey=ab050e7bb940586d7e7c36b6927e17e154c739f4 - with bid finding and no sanity
// https://prover.certora.com/output/11775/73a7d50d498649f8a16905450065ff88?anonymousKey=7050adce5c1bbad2670dc29c34d39add0cebc571 - wthi bid finding and basic sanity
// https://prover.certora.com/output/11775/26b7314f513d4f95bffb0f48614cf517?anonymousKey=d12c2e2c62cfe013d5b73785f95ff9232727a8a8 - with bid known and basic sanity
invariant atlasEthBalanceEqSumAccountsSurchargeMetacall()
    nativeBalances[currentContract] == sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
        filtered { f -> f.selector == sig:metacall( Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector}
        {
            preserved metacall(Atlas.UserOperation userOp, Atlas.SolverOperation[] solverOps, Atlas.DAppOperation dAppOp, address gasRefundBeneficiary) with (env e) {
                // assuming that Atlas is not the caller
                require e.msg.sender != currentContract;
                }
        }

// for execute function
// https://prover.certora.com/output/11775/3da8634f6548446fb65f65ee1dc0eb35?anonymousKey=bb6a848abf9cd7238d39426237cd14bda56da175 - with exPostBids, _bidFindingIteration and _bidKnownIteration NONDET
// https://prover.certora.com/output/11775/a960b28684e24c36827d3575f5ee6598?anonymousKey=144a46a5b20dd8666af0a3d1e2328775d65a56d9 - with postOpsCall in dispatch list
// https://prover.certora.com/output/11775/48e8fb41013648debba426076aa5b96e?anonymousKey=b7e30fa6dd189fdf10d6567187d7b93343e3813d - with bid known path and no sanity
// https://prover.certora.com/output/11775/aca718bfe7e94771a5b96f4b5b602477?anonymousKey=9c425d7dca383cb21eec7d0341d23954a36cba8b - with bid find path and no sanity
// https://prover.certora.com/output/11775/af8031d343014ca29ae61ff79f24a94e?anonymousKey=a4525b61e17e8b336dd887f27c1ea0c7e26be03d - with bid find path and basic sanity
// https://prover.certora.com/output/11775/159bb22d61684f1f92025d29e56aad1a?anonymousKey=750d818efe1ce064c8ea94b3e62be359010ab0e0 - with bid known path and basic sanity
invariant atlasEthBalanceEqSumAccountsSurchargeExecute()
    nativeBalances[currentContract] == sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
        filtered { f -> f.selector == sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool).selector}
        {
            preserved with (env e) {
                // assuming that Atlas is not the caller
                require e.msg.sender != currentContract;
                }
        }

// other functions
// https://prover.certora.com/output/11775/c76e5141631b4fbaadd2620b22aa9a6d?anonymousKey=055d94550e24db26281eb386e79105c00dbd2850 - with basic sanity and bid known path
// https://prover.certora.com/output/11775/584f8c0d97fa4a589e03421b7468974c?anonymousKey=50530dfc376124a4fab7c3890398e9e5b684d6b1 - wtih basic sanity and bid find path
// https://prover.certora.com/output/11775/71b8335af2dc44a0b5aeee5a0c52f3df?anonymousKey=83366ad7e77023f39c6575c83b6da6e2de52d9b8 - with no sanity and bid find path
// https://prover.certora.com/output/11775/d5aa2f64f61d4e9a8076311184ed52c4?anonymousKey=4f289c6e14134164b9d2ba6982501f9e30e91297 - with no sanity and bid known path
invariant atlasEthBalanceEqSumAccountsSurchargeOtherFunctions()
    nativeBalances[currentContract] == sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
        filtered { f -> f.selector != sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool).selector &&
                        f.selector != sig:metacall( Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector}
        {
            preserved with (env e) {
                // assuming that Atlas is not the caller
                require e.msg.sender != currentContract;
                }
        }

// for getExecutionEnvironment(address,address) function
// https://prover.certora.com/output/11775/53f3501c66be4faebc01e6b5c67072c6?anonymousKey=69b3b5df5929d29bbf86bed08a8f9fad44e34df4 - with exPostBids, _bidFindingIteration and _bidKnownIteration NONDET
invariant atlasEthBalanceEqSumAccountsSurchargegetExecutionEnvironment()
    nativeBalances[currentContract] == sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
        filtered { f -> f.selector == sig:getExecutionEnvironment(address,address).selector}


// modified invariant to check balance >=

// https://prover.certora.com/output/11775/6ccaeebfa0894f0cb2a512c70c3bc8c2?anonymousKey=9785ac0483cbb9ad503cc57769d04240dae584cb - with metacall filter -  violated due to havocing in create2 call; removed the DISPATCH list and trying again
// https://prover.certora.com/output/11775/409a58b80ad949439469622790d9cec7?anonymousKey=6a9e0f42ec2dfb87510a8d461dbf30bc344d8428 - without the dispatch list to avoid havocing in create2
// https://prover.certora.com/output/11775/f65859aaa51940788caf06d2d48b4702?anonymousKey=43da937c1e1a13a12545eb5b667b16196fb4b1d6 - with dispatch list for Escrow calls
// https://prover.certora.com/output/11775/7afc221877ed48dba7b0770c961158e1?anonymousKey=ba47b734768db1245cf540e2c7aec6b98772fd75 - with the munging in getOrCreateExecutionEnvironment (FactoryLib) to avoid create2
// https://prover.certora.com/output/11775/b13d7a20d50544849c1c14badca830c5?anonymousKey=7cf524680e86a0004f0c5f18bfed0c3fcbcfae80 - changed Escrow._ to _._ since the previous list didn't get applied
// https://prover.certora.com/output/11775/db4095ead2bc4e81a2bf17ad02025028?anonymousKey=efcfb23ad003ca7ec08e69ddb531768e084ae516 - without _bidFindingIteration and _bidKnownIteration NONDET
// https://prover.certora.com/output/11775/e212b5c2c2e64dce896d51af3b7343f3?anonymousKey=3dda23b28ec2a48e3e92e4080f4d275e5c318635 - with verifySolverOp and _checkSolverBidToken NONDET
// https://prover.certora.com/output/11775/5e9e28c07b584121b7ace6bf56ae2a63?anonymousKey=55b258fbe356560f366c3d81b4a178cda470c8e7 - with exPostBids ALWAYS(false) to pick _bidKnownIteration in line 172 in Atlas
// https://prover.certora.com/output/11775/4fa1ad0f923940b79b08a5284fcb4c43?anonymousKey=3b58796951931b56d976d12e64e988fa201323e7 - with _validateSolverOpDeadline and _checkTrustedOpHash NONDET
// https://prover.certora.com/output/11775/f84f620b5b8d42f2a4b110d89aae94b9?anonymousKey=603129ba2a124cbca018f468c9607b0b4f51d43a - with further simplification across the metacall function - killed
// https://prover.certora.com/output/11775/b310c27bb8cf4b9287fc18edaf400b94?anonymousKey=e1074d6204a31dae08385a8edb166db5dd9cda96 - above - math summaries
// https://prover.certora.com/output/11775/7d964201ddf0499eb313e95848aba794?anonymousKey=b65fde74967023a70756792486c72cebab5a4e24 - with loop iter 2
// https://prover.certora.com/output/11775/e3a6018c958e43e5a988572ae1fa92eb?anonymousKey=b8eb193ebf48462c4fb90d3a11ee2611625bd039 - with solverOps length > 0 - killed
// https://prover.certora.com/output/11775/f76c82a19e0f4ca088dda3eb3a604d3a?anonymousKey=a59c9278b56f4f4c405621ad144d8d74c040d27d - with John's patch
// https://prover.certora.com/output/11775/2e81cc3b58e04751801e5fb9a7e853f3?anonymousKey=8a16f2848229292f6606c66ae6e0c41d1017a92e - with msg.sender != atlas
// https://prover.certora.com/output/11775/c2cbb9e9893448feb74271d1ad0b69e8?anonymousKey=ba4f0702deeaacf68efe790d70e0224659f710cc - with loop iter 2
// https://prover.certora.com/output/11775/02e32a993a1944a995626bfb97fcd91e?anonymousKey=3790529e38b9107843b48bc2b9829c43334e57d1 - with getCalldataCost NONDET
// https://prover.certora.com/output/11775/1e2d3d8786ae48c5aff37aa3bba43475?anonymousKey=c6596b0f6635ae49c3f1f4ab6b24c523baa40659 - with getCalldataCost CONSTANT (900s)
// https://prover.certora.com/output/11775/c1d925a6fb2c495686cb53421e07d920?anonymousKey=1a40b71dc178297922658322f265011cd2cb62d8 - with 1800s
// https://prover.certora.com/output/11775/a8642c25ba904ad7944146ca14a31613?anonymousKey=3e3609ed93bd07a14dc97f7dfe9c162a56ec3386 - with 2 hr global timeout
// https://prover.certora.com/output/11775/6256bc9e17bd475b8a3e858566908da6?anonymousKey=db5d8348681cf7c6777c70be66ed02cf39427741 - with exPostBids NONDET to test both _bidFindingIteration and _bidKnownIteration paths
// https://prover.certora.com/output/11775/6091ae28412b4a21b1de2c761f07f570?anonymousKey=3ef1b5e6537fd9256a308454cb3dbbd2c5278e8b - without solverOps length > 0
// https://prover.certora.com/output/11775/d91b70c05a74456aaa0a50e34aeb80b7?anonymousKey=deb51bd12a69279a325537f64210e870790202d8 - with  solverOps length > 0 and exPostBids always true to test only _bidFindingIteration
// https://prover.certora.com/output/11775/0946c7989d574380a46f9f1f925c11a3?anonymousKey=0b8cfd754e1361b06ce6c94f64996d56da3c8a61 - with solver len>0, path false and sanity none
// https://prover.certora.com/output/11775/73ee229e4bc149d6964bf0bc22fd74de?anonymousKey=0adb2c69322caa06a16963f95ec2d27c35f413a7 - with parallel splitter conf
// https://prover.certora.com/output/11775/37e7095f63d943d3a29a8ab489251063?anonymousKey=ccd83a9a74ded42623f33e8be597e44968f9d927 - with Antti's branch and commit, without solver length require, bidKnownIteration only 
// https://prover.certora.com/output/11775/b4ddbefd257743d987f3c762dd1975b1?anonymousKey=1a22139b399504e31af6cae962cb33edc435e56f - with bidFindingIteration only and basic sanity
// https://prover.certora.com/output/11775/dc566062658a4401ba720551dbd01c8e?anonymousKey=8288b3e5dbf184780b9ef0c30689e19b0f9cd992 - with bidFindingIteration only and no sanity
// https://prover.certora.com/output/11775/e19c72e1393b4624a2d3a786b34cd25f?anonymousKey=07944fea814be682c8abf375a45d2cd415d125b4 - with atlasSolverCall callback to borrow in Atlas
invariant atlasEthBalanceGeSumAccountsSurchargeMetacall()
    nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
        filtered { f -> f.selector == sig:metacall( Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector}
        {
            preserved  with (env e) {
                // assuming that Atlas is not the caller
                require e.msg.sender != currentContract;
                }
        }

// Execute function
// https://prover.certora.com/output/11775/751694bbc0bd4b15abf525594f48badc?anonymousKey=6552aa78d66b08406dee536dd0d9f9018c8f678c - with basic sanity and bid find path
// https://prover.certora.com/output/11775/7bb5a350c8fd4751b1a3c4d51cf1ceaf?anonymousKey=4fa4feefc20ec04c2a32a52664fcd67cc112c635 - with basic sanity and bid known path
// https://prover.certora.com/output/11775/d1161cef8d974cffbe1bfad8014b6196?anonymousKey=54508ffd0573acd4f70dcb511fe6e6a40b835dc2 - with no sanity and bid known path
// https://prover.certora.com/output/11775/f56a3c8526d74209a1ab8a76010b3538?anonymousKey=09631420f55f8252a5616309505850a8894edbc0 - with no sanity and bid find path
// https://prover.certora.com/output/11775/9e877c6a020646b1a3173c10420b0e1a?anonymousKey=2da5b7b88715178ed4653974eb766785c3523503 - coverage info basic bid known and basic sanity
// https://prover.certora.com/output/11775/3ba4024f84894e978f378beda86a83d9?anonymousKey=d9f78f0f069a81054b4b6e43d73a9f2a37f72230 - coverage info basic bid known and no sanity
// https://prover.certora.com/output/11775/534164afcf4a4548864af7f044e320bb?anonymousKey=2b8bb91924e9b839bf4b68d394bce8105b315226 - coverage info basic bid find and no sanity
// https://prover.certora.com/output/11775/d86d5aaf2b244a8dbf4e7f64334d555a?anonymousKey=a3bb807aadc30a6734b36a5d8f0ed795ad0e80bd - coverage info basic bid find and basic sanity
// https://prover.certora.com/output/11775/0ba5fefcdb0a46b1a1b1e2dace92ed0a?anonymousKey=3e79b9339c9dd9f8932720a22a6f412a3010b1b4 - without preserved block bid known path
// https://prover.certora.com/output/11775/d4da4b863f2340e19e3f3c6af6242287?anonymousKey=1cf578c68ea9a7ca9ecdb2a479e9fff4280a8547 - without preserved block bid find path
invariant atlasEthBalanceGeSumAccountsSurchargeExecute()
    nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
        filtered { f -> f.selector == sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool).selector}

// other functions
// https://prover.certora.com/output/11775/74e3ddde2731421faa1233c7978255b9?anonymousKey=388291b7aecca9d57c3a10facee01f656bc4909a - with no sanity and bid known path
// https://prover.certora.com/output/11775/6c602f9c17d841e09ffed8f01a91da52?anonymousKey=10a055ccaea0e427e23fbc61f8ef361b35c871fe - with no sanity and bid find path
// https://prover.certora.com/output/11775/abf5969b9ca34366a4047db52bab0f72?anonymousKey=052cd87df0c399d0333244a0f239b5d1bc975489 - with basic sanity and bid find path
// https://prover.certora.com/output/11775/a094cbffd2774538853dd5c41565cfb2?anonymousKey=df1e5d7c3463c9734bcc57da24a20ffc36d57787 - with basic sanity and bid known path
// https://prover.certora.com/output/11775/6999c26eb16543ce86daf3b7597552e4?anonymousKey=db2c3fb305c7af0b24e9d1083a235109ba164d5b - bid known with coverage info basic to see source of vacuity in solverCall
// https://prover.certora.com/output/11775/57f7dc30ba844facbe8246fbef4222e4?anonymousKey=3ecffc24b6b743ba15bbebd04a9e98b14d3efa1f - bid find with coverage info basic to see source of vacuity in solverCall
// https://prover.certora.com/output/11775/4fc38a1dfac04a5486b2e9aae9872026?anonymousKey=3dacb27ded19c66e3e5214651a62eb9365581046 - bid known without preserved block
// https://prover.certora.com/output/11775/f4c75488e2734f9e91c856f40458975f?anonymousKey=3547cbd59711b78f34b8acb792b1e5a08606079d - bid find without preserved block
invariant atlasEthBalanceGeSumAccountsSurchargeOtherFunctions()
    nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
        filtered { f -> f.selector != sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool).selector &&
                        f.selector != sig:metacall( Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector}
        {
            preserved with (env e) {
                // assuming that Atlas is not the caller
                require e.msg.sender != currentContract;
                }
        }
// solverCall function
// https://prover.certora.com/output/11775/909fdf49ffbb40699f972f6029ba84fe?anonymousKey=4030e78a449d3678d87de9700a1d927208cc38af - with bid known path
// https://prover.certora.com/output/11775/230da475f45f459588a2fcd0b55cb5fa?anonymousKey=096ee1cb9a8e4a2b1507d553ec8982f3b28c1dfe - with bid find path
// https://prover.certora.com/output/11775/11c60f85e77542ae863cafaa13253fad?anonymousKey=2de67a4a68c3abe659e3596bcf93f9d0cf926cd7 - with coverage info and bid known path
// https://prover.certora.com/output/11775/14200893dcd74e668eb4b8ef20785b80?anonymousKey=4b06d9eab27ccb9bc40e33705f9aa3aa1069a8db - with coverage info and bid find path
invariant atlasEthBalanceGeSumAccountsSurchargeSolverCall()
    nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge
        filtered { f -> f.selector == sig:solverCall(Atlas.Context, Atlas.SolverOperation, uint256 ,bytes).selector}
        // {
        //     preserved with (env e) {
        //         // assuming that Atlas is not the caller
        //         require e.msg.sender != currentContract;
        //         }
        // }


// Rule checking the invariant with borrow and reconcile 
// https://prover.certora.com/output/11775/907d46ed060d455f8ecbef92819d5320?anonymousKey=9273000b61e6497ec451022dfc54ad9d8990542d - first run - violation
// https://prover.certora.com/output/11775/41e8c4bc085a4160b30e6473f49a7249?anonymousKey=87f4f125a08b055c6e8e6ba05b3747f4a7e35013 - with solverOps length > 0 - OOM
rule borrowReconcileInvCheck(){

    env e;
    require e.msg.sender != currentContract;
    require nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;

    Atlas.UserOperation userOp;
    Atlas.SolverOperation[] solverOps;
    Atlas.DAppOperation dAppOp;
    address gasRefundBeneficiary;

    require solverOps.length == 1;

    metacall(e, userOp, solverOps, dAppOp, gasRefundBeneficiary);
    
    assert nativeBalances[currentContract] >= sumOfBonded + sumOfUnbonded + sumOfUnbonding + currentContract.S_cumulativeSurcharge + deposits - withdrawals;
}

// sanity rule to resolve calls for metaCall
// https://prover.certora.com/output/11775/f6240b9bce724559bbd05cfa297096be?anonymousKey=3342008d04da9f0f48b25561dfe9ce85c0b7aaef - with DIPATCH list summary for LIB delegate call
// https://prover.certora.com/output/11775/7371125e2302477190e7272e171c6650?anonymousKey=cd097c4e3a4e9c2285b8a0d52c7ec1ceb76fcc60 - with Atlas instead of current contract in summary
// https://prover.certora.com/output/11775/4ab9f279824b456e8ad802ddb90efa92?anonymousKey=e7ac1fc87c473a8069f330b02d1ef51e325fac48 - with wildcard in summary for delegate call
// https://prover.certora.com/output/11775/5e68fa4dde4e4cbaa2bdbf05189f5da5?anonymousKey=ecbca3cd825f7f7e540661646730eac8bd3d6223 - with _._ in the summary
// https://prover.certora.com/output/11775/a325ddb031f14f6396497b8dae885e82?anonymousKey=6327f1a66a5240beb45114c82dcbc3177c1f2c99 - with Atlas._ in the summary
// https://prover.certora.com/output/11775/5c0698743ea44c88a6053fb17f30a8ed?anonymousKey=19f204d85795341156e33f719edef056e2a5cdee - wtih execute and validateCall in DISPATCH list
// https://prover.certora.com/output/11775/009c1ec36f004130ae900b9ad5e97e0d?anonymousKey=c83854267e95734ebf4144f0a523c85b0c29914d - above + maxCommandCount 1e9
// https://prover.certora.com/output/11775/0bd9ab8b79094a2ab89a0b15b41bce12?anonymousKey=9c198bfd6285c1418570334bf34522d48f8246bd - with maxBlockCount 1e9
// https://prover.certora.com/output/11775/23b68f2aaaba4e728c5d2aa51d0b851a?anonymousKey=078bd9257a2c60606752b2b770b924cd94ef6663 - with --optimistic_fallback to see if solves the safeTransferEth unresolved call - hardstop timeout
// https://prover.certora.com/output/11775/d2d51f9a01164821bbb9cfa43b5e04ec?anonymousKey=99e6833a8929e19ca69c6df02cdd9391b06151ba - with optimistic_fallback and no functions in DISPATCH list to avoid timeout
// https://prover.certora.com/output/11775/bc8f7844c66d456a858093c62d65c4f1?anonymousKey=eecb919a471f955ab882f03d74626698a79255bc - with validateCall only in DISPATCH list
// https://prover.certora.com/output/11775/97d7a2747a3449baaed280b6fc133e4f?anonymousKey=19701ffec8c03201ed7269dc5e612d34f678931e - wtih execute only in the DISPATCH list
// https://prover.certora.com/output/11775/2feb10306be94b4da365807a92fd8aca?anonymousKey=6414786e18589d1cc60515c9c8e0e05281704fa4 - with safeTransferETH body commented out to see if it helps with memory/pointer analysis failure
// https://prover.certora.com/output/11775/9d0cb8604a744df8bf80b6eabc7f4c45?anonymousKey=5d5fec30d16cf3d26fc35c7779d9fb3424f99dcc - wtih CVL summary for safeTransferLib
// https://prover.certora.com/output/11775/a1551b26119e456e97b6a2f2e6c85c04?anonymousKey=ce4b6a90622d200e56101e6562d71e1c230354fc - with _getMimicCreationCode commented out and safeTransferLib summarized
// https://prover.certora.com/output/11775/b97472cedd1b409881abd74fdf0e5258?anonymousKey=17fd2b37113cfe013459fb4bbcaed58579c55aff - with computeSalt NONDET and try catch munging
// https://prover.certora.com/output/11775/5974e1fc873e4a9d9faa42d342d0105b?anonymousKey=4e1ad733d20d157ee53b617437b74ada523720ad -  above but munging comments out _settle as well
// https://prover.certora.com/output/11775/6a74f2ffbc464b7083213018d148a378?anonymousKey=85fe6fe9ff4f3f5b671b265186d9c1ce8e6761b7 - with john's branch
// https://prover.certora.com/output/11775/1c7374e5986f4558afb8e8b6e6c98f83?anonymousKey=1d1253934d29fe1fa3e3f65d54f8b2c3889f285c - with smt timeout 7200

rule metaCallSanity(){
    env e;
    calldataarg args;
    metacall(e, args);
    assert false;
}

// https://prover.certora.com/output/11775/6459705ca8b94b33a350f5ad6123893c?anonymousKey=46225a937e85043dc2bb1332983a0eb5a37f81e5
// https://prover.certora.com/output/11775/97a8e9d3f7d6463e9ed80a87c28a5ea8?anonymousKey=79373cb1918023de1dff7c94d26c4a892da8d977 - with _executePreOpsCall specific DISPATCH list for encodeCall in Escrow.sol line 68
// https://prover.certora.com/output/11775/aa0a837b45a944f5999cb799b5787fd1?anonymousKey=e89a6c692e74abde632cd2256f3f8533b27f193a - with _executePreOpsCall specific DISPATCH list for encodeCall in Escrow.sol line 116 userWrapper
rule executeSanity(){
    env e;
    calldataarg args;
    execute(e, args);
    assert false;
}

// https://prover.certora.com/output/11775/a93d41da24d44e08b5f3a392f7a515d1?anonymousKey=4a8b72297d6826592a43defa93074884e216df23
rule validateCallsSanity(){
    env e;
    calldataarg args;
    AtlasVerification.validateCalls(e, args);
    assert false;
}
 
// https://prover.certora.com/output/11775/65bc5d67287b4552a6c8ef0d01302b84?anonymousKey=325f231ecc2a03dc4c9941400eb4a77c2e306567 -  with solveCall in DISPATCH_LIST to resolve call in line 594 of Escrow.sol (CERT-7540) -  hardstop
// https://prover.certora.com/output/11775/87ed6a873be9485b96cef685ea9299be?anonymousKey=020ec53bdaa998d7b4c7a996efbc4d3fbbaf7882 - with only solverPreTryCatch in the DISPATCH list
// https://prover.certora.com/output/11775/52219c526f164dadbdae7411e08ac73d?anonymousKey=7a192f0d70db13051d90b594f99b97549c72d56c - with solverPreTryCatch and atlasSolverCall in DISPATCH list
// https://prover.certora.com/output/11775/7ef89ab4298a4b3296cc0265252e8ecb?anonymousKey=6efd16d237e1a7412191631435bc2249f0bbf4e2 - with only atlasSolverCall in DISPATCH list
// https://prover.certora.com/output/11775/b4356699d7544b58909abc7d1c2bfdcc?anonymousKey=edb45c71bcd9285aeb1bffe7a393c16054d77b01 - sample run for JFR report
rule solverCallSanity(){
    env e;
    calldataarg args;
    solverCall(e, args);
    assert false;
}



// lock() always returns 0
// https://prover.certora.com/output/11775/321181016f0149538eb6db686a8c0eb1?anonymousKey=dd5221a1fd2ee2b0d1561d0dfd015df054835860 -  hardstop
invariant lockReturnsZero()
    getLockEnv() == 0 && getLockCallConfig() == 0 && getLockPhase() == 0
        {
            preserved with (env e) {
                // assuming that Atlas is not the caller
                require e.msg.sender != currentContract;
                }
        }

// metacall
// https://prover.certora.com/output/11775/c98b238b2be54b84a4f3aa3c1985b317?anonymousKey=a221e5f34dc872bba55e1ce8c6539c35cf1ab164 - hardstop
// https://prover.certora.com/output/11775/37c244355ede45ee8b83e783a43fd62e?anonymousKey=a632b08c596777246591af90c9c9efcdbb2971a7 - with preserved block - OOM
// 
invariant lockReturnsZeroMetacall()
    getLockEnv() == 0 && getLockCallConfig() == 0 && getLockPhase() == 0
    filtered {f -> f.selector == sig:metacall(Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector}
        {
            preserved with (env e) {
                // assuming that Atlas is not the caller
                require e.msg.sender != currentContract;
                }
        }

// Execute
// https://prover.certora.com/output/11775/30f790c1d72d4b06954b83f6455bc967?anonymousKey=e155aa6717271fb2a1313fe3187ff2fd4879c5b1 - first run
// https://prover.certora.com/output/11775/ad61a51a57bc49c98e4af9c54efa7d5c?anonymousKey=9aec13fb90e04a45f2d197be965d5d8c15de4be5 - with preserved block - VACUOUS
invariant lockReturnsZeroExecute()
    getLockEnv() == 0 && getLockCallConfig() == 0 && getLockPhase() == 0
    filtered { f -> f.selector == sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool).selector}
        {
            preserved with (env e) {
                // assuming that Atlas is not the caller
                require e.msg.sender != currentContract;
                }
        }

// Other functions
// https://prover.certora.com/output/11775/4b67ebaec3f8423a8535d1ea336e269b?anonymousKey=f1d50fa70def0a8ed5ea910c35c82bc66b7459f5 - first run
// https://prover.certora.com/output/11775/6ea23b968377480693f7609bee4b70ae?anonymousKey=94489c5925564119e0a260649726163c67f6a8ba - with preserved block - VACUOUS
invariant lockReturnsZeroOtherFunctions()
    getLockEnv() == 0 && getLockCallConfig() == 0 && getLockPhase() == 0
    filtered { f -> f.selector != sig:execute(Atlas.DAppConfig, Atlas.UserOperation, Atlas.SolverOperation[], address, address, bytes32, bool).selector &&
                        f.selector != sig:metacall( Atlas.UserOperation, Atlas.SolverOperation[], Atlas.DAppOperation, address).selector}
        {
            preserved with (env e) {
                // assuming that Atlas is not the caller
                require e.msg.sender != currentContract;
                }
        }