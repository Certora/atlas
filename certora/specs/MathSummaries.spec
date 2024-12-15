methods
{
	// 
	
	function AccountingMath.withSurcharge(uint256 a, uint256 b) internal returns (uint256) => CVLwithSurcharge(a, b);
	function AccountingMath.withoutSurcharge(uint256 a, uint256 b) internal returns (uint256) => CVLwithoutSurcharge(a, b);
	function AccountingMath.getSurcharge(uint256 a, uint256 b) internal returns (uint256) => CVLgetSurcharge(a, b);
	function AccountingMath.getPortionFromTotalSurcharge(uint256 a, uint256 b, uint256 c) internal returns (uint256) => CVLmulDiv(a, b, c);
	function AccountingMath.maxBundlerRefund(uint256 a) internal returns (uint256) => CVLmaxBundlerRefund(a);
	function _.sqrt(uint256 x) internal => CVL_sqrt(x) expect uint256;
	

}

function CVLwithSurcharge(uint256 a, uint256 b) returns uint256 {
	return require_uint256(a * (10^7 + b) / 10^7);
}

function CVLwithoutSurcharge(uint256 a, uint256 b) returns uint256 {
	return require_uint256(a * 10^7 / (10^7 + b));
}

function CVLgetSurcharge(uint256 a, uint256 b) returns uint256 {
	return require_uint256(a * b / 10^7);
}

function CVLmaxBundlerRefund(uint256 a) returns uint256 {
	return require_uint256(a * 8*10^6 / 10^7);
}


function CVLmulDiv(uint256 a, uint256 b, uint256 c) returns uint256 {
	require c != 0;
	return require_uint256(a * b / c);
}

function CVLmulDivRoundingUp(uint256 a, uint256 b, uint256 c) returns uint256 {
	require c != 0;
	return  require_uint256((a * b + c - 1) / c);
}

// function CVLmulDivWithRounding(uint256 a, uint256 b, uint256 c, Math.Rounding rounding) returns uint256 {
// 	require c != 0;
// 	if (rounding == Math.Rounding.Expand)
// 		return CVLmulDivRoundingUp(a, b, c);
// 	return 0;
// }


/*
persistent ghost CVL_lsb(uint256) returns uint8 {
	axiom forall uint256 x. forall uint256 pow. forall uint256 pow_minus.
		pow == 2^CVL_lsb(x)
		&& pow_minus == 2^(CVL_lsb(x) - 1)
        && x & pow != 0 
		&& x & pow_minus == 0;
}
*/

function CVL_sqrt(uint256 x) returns uint256 {
    mathint SQRT;
    require SQRT*SQRT <= to_mathint(x) && (SQRT + 1)*(SQRT + 1) > to_mathint(x);
    return require_uint256(SQRT);
}

ghost mapping(bytes32 => mapping(uint => bytes32)) sliceGhost;

function bytesSliceSummary(bytes buffer, uint256 start, uint256 len) returns bytes {
	bytes to_ret;
	require(to_ret.length == len);
	require(buffer.length >= require_uint256(start + len));
	bytes32 buffer_hash = keccak256(buffer);
	require keccak256(to_ret) == sliceGhost[buffer_hash][start];
	return to_ret;
}
