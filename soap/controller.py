from spyne import ServiceBase, Unicode, rpc, Boolean
import random


class TransactionController(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Boolean)
    def complete_transaction(ctx, card_no, name, expiry, price):
        # get success of the transaction
        print("IN SOAP SERVER")
        success = True
        no = random.random()
        if no > 0.9:
            success = False
        if success:
            print("Transaction Success")
            return 1
        else:
            print("Transaction Failed")
            return 0
