from web3.exceptions import TimeExhausted

from .utils import ADDRS, CONTRACTS, KEYS, deploy_contract, send_transaction, wait_for_transaction_receipts


def test_gas_eth_tx(geth, ethermint):
    tx_value = 10

    # send a transaction with geth
    geth_gas_price = geth.w3.eth.gas_price
    tx = {"to": ADDRS["community"], "value": tx_value, "gasPrice": geth_gas_price}
    geth_receipt = send_transaction(geth.w3, tx, KEYS["validator"])

    # send an equivalent transaction with ethermint
    ethermint_gas_price = ethermint.w3.eth.gas_price
    tx = {"to": ADDRS["community"], "value": tx_value, "gasPrice": ethermint_gas_price}
    ethermint_receipt = send_transaction(ethermint.w3, tx, KEYS["validator"])

    # ensure that the gasUsed is equivalent
    assert geth_receipt.gasUsed == ethermint_receipt.gasUsed


def test_gas_deployment(geth, ethermint):
    # deploy an identical contract on geth and ethermint
    # ensure that the gasUsed is equivalent
    _, geth_contract_receipt = deploy_contract(
        geth.w3,
        CONTRACTS["TestERC20A"])
    _, ethermint_contract_receipt = deploy_contract(
        ethermint.w3,
        CONTRACTS["TestERC20A"])
    assert geth_contract_receipt.gasUsed == ethermint_contract_receipt.gasUsed


def test_gas_call(geth, ethermint):
    function_input = 10
    geth_gas_price = geth.w3.eth.gas_price
    ethermint_gas_price = ethermint.w3.eth.gas_price

    # deploy an identical contract on geth and ethermint
    # ensure that the contract has a function which consumes non-trivial gas
    geth_contract, _ = deploy_contract(
        geth.w3,
        CONTRACTS["BurnGas"])
    ethermint_contract, _ = deploy_contract(
        ethermint.w3,
        CONTRACTS["BurnGas"])

    # get the call reciepts
    geth_txhash = (geth_contract.functions
                   .burnGas(function_input)
                   .transact({'from': ADDRS["validator"], "gasPrice": geth_gas_price}))
    geth_call_receipt = wait_for_transaction_receipts(geth.w3, [geth_txhash])[0]

    ethermint_txhash = (ethermint_contract.functions
                   .burnGas(function_input)
                   .transact({'from': ADDRS["validator"], "gasPrice": ethermint_gas_price}))
    ethermint_call_receipt = wait_for_transaction_receipts(ethermint.w3, [ethermint_txhash])[0]

    # ensure that the gasUsed is equivalent
    assert geth_call_receipt.gasUsed == ethermint_call_receipt.gasUsed
