from flask import Flask, jsonify, request, make_response
from datetime import datetime
import logging
import secrets
import requests
import mysql.connector


app = Flask(__name__)


response = requests.get('https://blockchain.info/ticker')
exchange_rates = response.json()
rate = exchange_rates['EUR']['last']


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kood',
    'database': 'bitcoin_wallet',
}


def execute_query(query, values=None, fetchall=False):
    try:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor(dictionary=True) as cursor:
                logging.info(f"Executing query: {query}, values: {values}")
                cursor.execute(query, values)
                if fetchall:
                    return cursor.fetchall()
                else:
                    return cursor.fetchone()
    except mysql.connector.Error as err:
        error_message = f"Database error: {err}"
        logging.error(f"Error executing query: {query}, values: {values}. Details: {err}")
        raise RuntimeError(error_message)


@app.route('/transactions', methods=['GET'])
def list_transactions():
    try:
        logging.info("Connecting to the database for listing transactions.")
        transactions = execute_query('SELECT * FROM transactions', fetchall=True)

        if not transactions:
            return jsonify({"error": "No transactions found"}), 404

        return jsonify(transactions), 200
    except RuntimeError as e:
        logging.error(f"Error in list_transactions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        logging.info("Connecting to the database for retrieving balance.")
        result = execute_query('SELECT SUM(amount_btc) AS total_balance FROM transactions WHERE spent = FALSE')

        if result["total_balance"] is None:
            logging.info("No transactions found for balance.")
            return jsonify({"BTC": 0.0, "EUR": 0.0}), 200
        else:
            total_balance_btc = float(result['total_balance'])
            total_balance_eur = round(total_balance_btc * rate, 2)
            logging.info(f"Balance retrieved successfully. BTC: {total_balance_btc}, EUR: {total_balance_eur}")
            return jsonify({"BTC": total_balance_btc, "EUR": total_balance_eur}), 200

    except RuntimeError as e:
        logging.error(f"Error in get_balance: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/transfer', methods=['POST'])
def create_transfer():
    amount_str = request.form.get('amount_eur')

    if amount_str is not None and float(amount_str) > 0:
        try:
            amount_eur = float(amount_str)
        except ValueError:
            return jsonify({"error": "Invalid amount format"}), 400
    else:
        return jsonify({"error": "Amount not provided"}), 400

    amount_btc = amount_eur/rate
    logging.info(f"Amount in EUR: {amount_eur}, Amount in BTC: {amount_btc}")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM transactions WHERE spent = FALSE ORDER BY amount_btc ASC')
        unspent_transactions = cursor.fetchall()
    except RuntimeError:
        return jsonify({"error": "Database not found"}), 500

    total_unspent_balance_btc = float(sum(transaction['amount_btc'] for transaction in unspent_transactions))

    if amount_btc > total_unspent_balance_btc or amount_btc < 0.00001:
        logging.warning("Not enough balance for the transfer.")
        return jsonify({"error": "Not enough balance for the transfer"}), 400

    spent_transactions = []
    remaining_balance = amount_btc

    for transaction in unspent_transactions:
        if remaining_balance > 0:
            remaining_balance -= float(transaction['amount_btc'])
            spent_transactions.append(transaction)
        else:
            break

    new_transaction = {}
    if remaining_balance < 0:
        new_transaction = {
            'id': secrets.token_hex(16),
            'amount_btc': abs(remaining_balance),
            'spent': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    for spent_transaction in spent_transactions:
        cursor.execute('UPDATE transactions SET spent = TRUE WHERE id = %s', (spent_transaction['id'],))

    conn.commit()
    conn.close()

    if len(new_transaction) != 0:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('INSERT INTO transactions (id, amount_btc, spent, created_at) VALUES (%s, %s, %s, %s)',
                       (new_transaction['id'], new_transaction['amount_btc'], new_transaction['spent'],
                        new_transaction['created_at']))

        conn.commit()
        conn.close()

    logging.info("Transfer successful.")
    return jsonify({"message": "Transfer successful"}), 200


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000, debug=True)

