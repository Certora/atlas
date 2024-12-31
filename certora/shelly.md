yarn
git submodule init
git submodule update
cd certora
make munged

# need to define a process for fixing dependencies

atlasEthBalanceGeSumAccountsSurchargeTransientMetacallRule
invariant atlasEthBalanceGeSumAccountsSurcharge* - 4 cases
    metacall requires reentrancy
        try to havoc / strong invariant