# records/signals.py
from records.models import TransactionItem

def apply_transaction_impact(transaction_obj, action="apply"):
    """
    雙軌平帳核心 Helper 函式
    :param action: "apply" (套用影響) 或 "revert" (撤銷影響)
    """
    multiplier = 1 if action == "apply" else -1
    t_type = transaction_obj.transaction_type
    amount = transaction_obj.total_amount

    # ==========================================
    # 實體帳戶 (Account) 平帳
    # ==========================================
    # 來源帳戶 (account)
    account = transaction_obj.account
    if account:
        account.refresh_from_db()
        if t_type == 'expense':
            account.balance -= (amount * multiplier)
        elif t_type == 'income':
            account.balance += (amount * multiplier)
        elif t_type == 'transfer':
            # 轉帳：來源帳戶 (例如：銀行) 扣錢
            account.balance -= (amount * multiplier)
        account.save()

    # 轉帳專屬：目標帳戶 (to_account)
    to_account = getattr(transaction_obj, 'to_account', None)
    if t_type == 'transfer' and to_account:
        to_account.refresh_from_db()
        # 轉帳：目標帳戶 (例如：現金) 加錢
        to_account.balance += (amount * multiplier)
        to_account.save()

    # ==========================================
    # 聯絡人 (Contact) 實時平帳
    # ==========================================
    # 轉帳通常不涉及聯絡人；一般收支才會處理聯絡人
    if t_type in ['expense', 'income']:
        items = TransactionItem.objects.filter(transaction=transaction_obj)
        for item in items:
            contact = item.contact
            if not contact:
                continue

            contact.refresh_from_db()
            item_charge = item.selling_amount if item.selling_amount is not None else item.amount

            if t_type == 'expense':
                # 代購/墊付款：對方欠款增加 (+)
                contact.balance += (item_charge * multiplier)
            elif t_type == 'income':
                # 還款/收款：對方欠款減少 (-)
                contact.balance -= (item_charge * multiplier)

            contact.save()