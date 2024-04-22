# Backend Services & API Internship Assignment

## Setup

The API needs a MySQL server to store and fetch data from. To use the API the local system has to have a MySQL server installed. The most simple version of that server can be found here: 

```text
https://dev.mysql.com/downloads/mysql/
```

The database has to have this kind of table in it:

```text
CREATE TABLE `transactions` (
  `id` varchar(255) NOT NULL,
  `amount_btc` decimal(10,8) DEFAULT NULL,
  `spent` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
)
```

The API has to also supply valid credentials to access the database, the credentials can be altered on rows `17-21`:

```text
db_config = {
    'host': 'localhost', # The name of the system
    'user': 'root', # The name of the MySQL user
    'password': 'kood', # Password for the server
    'database': 'bitcoin_wallet', # Name of the database
}
```

## Use

The API can be used with a browser and with the `create_transfer.py` program that I included in the repository. With the browser, the API can be accessed through `http://localhost:5000/transactions` and `http://localhost:5000/balance` which create respective JSON files. since transfers require input it can't simply be accessed through the browser without a front-end solution and therefore I wrote a small program that allows users to input amounts into the API.

There is also a small `test_queries.py` file that tests for the basic functions of the API.
