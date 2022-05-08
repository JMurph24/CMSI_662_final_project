import sqlite3

#It handles user's account such as getting the balance and doing the transfer
#The function gets the balance of logged in user from the database bank of the table named accounts  
def get_balance(account_number, owner):
    try:
        con = sqlite3.connect('bank.db')
        cur = con.cursor()
        cur.execute('''
            SELECT balance FROM accounts where id=? and owner=?''',
                    (account_number, owner))
        row = cur.fetchone()
        if row is None:
            return None
        return row[0]
    finally:
        con.close()

#Transfer the amount from the source account to target account and updates it to the bank database
def do_transfer(source, target, amount):
    try:
        con = sqlite3.connect('bank.db')
        cur = con.cursor()
        cur.execute('''
            SELECT id FROM accounts where id=?''',
                    (target,))
        row = cur.fetchone()
        if row is None:
            return False
        cur.execute('''
            UPDATE accounts SET balance=balance-? where id=?''',
                    (amount, source))
        cur.execute('''
            UPDATE accounts SET balance=balance+? where id=?''',
                    (amount, target))
        con.commit()
        return True
    finally:
        con.close()
