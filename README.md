# Python Mpesa SDK

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/PhilipWafula/python-mpesa-sdk/ci.yml)
![Codecov](https://img.shields.io/codecov/c/github/PhilipWafula/python-mpesa-sdk)
![GitHub](https://img.shields.io/github/license/PhilipWafula/python-mpesa-sdk)
![GitHub release (release name instead of tag name)](https://img.shields.io/github/v/release/PhilipWafula/python-mpesa-sdk)



Welcome to the Mpesa Python SDK. This is a Python wrapper for the Safaricom Daraja API.
It simplifies the process of integrating your Python applications, frameworks, and libraries with the Daraja API.

## Features
The Mpesa Python SDK currently supports the following Mpesa services:

1. Mpesa Express (STK Push)
2. C2B Transactions
3. B2C Transactions
4. Transaction Status Queries
5. Reverse Transaction Requests

## Pre-requisites
To use the SDK, you need to have:

- A [Safaricom Developer](https://developer.safaricom.co.ke/) account.
- A registered app on the [Safaricom Developer](https://developer.safaricom.co.ke/) portal.
- An app consumer key and consumer secret.
- A registered Mpesa-enabled SIM card.
- Python 3.10 or higher.
- [Poetry](https://python-poetry.org/) for dependency management.

## Installation
To install the SDK, run the following command:

```bash
pip install python-mpesa-sdk
```

or
```bash
poetry add mpesa-
```

## Usage
This SDK requires the definition of the environment variables as described in the .env.example file. Ensure these
variables are defined in your environment before using the SDK.


Here is a simple example of how to use the SDK to make a B2C transaction request:

```python
# external imports
from mpesa_sdk.daraja.b2c import B2CPaymentRequest, B2CPaymentResponseParser
from mpesa_sdk.daraja.enums import CommandID

# create an instance of the B2CPaymentRequest class
b2c = B2CPaymentRequest('100', CommandID.BUSINESS_PAYMENT, 'Operator', 'Jun-17062023-IN-00200C', 'ShortCode', '2547XXXXXXXX', 'Remarks')

# make the request
response = b2c.execute()
print(f'Response: {response}')

# create an instance of the B2CPaymentResponseParser class
b2c_parser = B2CPaymentResponseParser(response)

# parse the response into a python dictionary
parsed_response = b2c_parser.parse()
print(f'Parsed response: {b2c_parser.response}')
```

## Documentation
For more information about the SDK, check out the [Wiki](https://github.com/PhilipWafula/mpesa-python-sdk/wiki)

## Contribution
Contributions to the Python Mpesa SDK are always welcome. If you want to contribute, please take a moment to review the
[contributing guidelines](CONTRIBUTING.md) to get a feel for the coding standard and development workflow.

## License
This project is licensed under the WTFPL License - see the [LICENSE](LICENSE) file for details.

## Disclaimer
This SDK is not officially affiliated with Safaricom. Use it at your own risk. Always ensure that you adhere to the
terms and conditions provided by Safaricom for use of their Daraja API.
