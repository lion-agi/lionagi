
# LionAGI Branch Tutorial: Working with Structured Outputs using Forms

## Introduction

This tutorial extends the basic usage of the `Branch` class in the LionAGI framework by introducing how to work with structured outputs using forms. You'll learn how to define forms, use them to input structured data, and retrieve structured outputs from the assistant.

## Table of Contents

1. [Setting Up the Environment](#setting-up-the-environment)
2. [Defining Enums and Forms](#defining-enums-and-forms)
3. [Using Forms to Calculate Total Amount](#using-forms-to-calculate-total-amount)
4. [Using Forms to Determine Repair Service Cost](#using-forms-to-determine-repair-service-cost)
5. [Conclusion](#conclusion)

## Setting Up the Environment

To begin, we need to import the necessary modules from the LionAGI package.

### Example Usage

The following code demonstrates how to import LionAGI.

```python
import lionagi as li
```

## Defining Enums and Forms

Enums and forms are used to define structured data within a branch. Here, we define bike models and repair services as enums and use them in a form to handle bike repair invoices.

### Example Usage

The following code demonstrates how to define enums for bike models and repair services, and how to create a form for a bike repair invoice.

```python
from enum import Enum

class BikeModel(int, Enum):
    TIERA = 200
    TIERB = 100
    TIERC = 50

class RepairService(int, Enum):
    DEFAULT_REPAIR = 100
    PREMIUM_REPAIR = 200
    EXPRESS_REPAIR = 300

class BikeRepairInvoice(li.Form):
    assignment: str = "bike_price, repair_price -> total_amount"
    total_amount: float = li.Field(None, description="The total amount of the invoice.")
    bike_price: Enum | int = li.Field(
        None, keys=BikeModel, description="The price of a specific bike model."
    )
    repair_price: Enum | int = li.Field(
        None, keys=RepairService, description="The price of a specific repair service."
    )
```

## Using Forms to Calculate Total Amount

We can use the defined form to calculate the total amount of a bike repair invoice by providing the bike price and repair service price.

### Example Usage

The following code demonstrates how to calculate the total amount for a bike repair invoice.

```python
instruction = """
calculate the total amount of a bike repair invoice using the bike price and repair service price.
"""

# Create an instance of the form with specified bike and repair prices
form = BikeRepairInvoice(bike_price=200, repair_price=100)

# Create a new branch and send the instruction along with the form
branch = li.Branch()
b = await branch.chat(instruction=instruction, form=form)

# Retrieve the last message from the branch
branch.messages[-1]
# Output: Message(role=assistant, sender=eab05e5cca9f1d08ea15b8ebf7fa66b5, content='{'assistant_response': "\`\`\`json\n{'total_amount': 300}\n\`\`\`"}')

# Get the assistant's response content
branch.messages[-1].content
# Output: {'assistant_response': "\`\`\`json\n{'total_amount': 300}\n\`\`\`"}

# Convert the response to a dictionary for further inspection
b.to_dict()
# Output: {'ln_id': '6995cd79825803d63b75b56825a3f952', 'created': '2024-05-14T02:08:41.578413', 'metadata': {...}, 'total_amount': 300, 'bike_price': 200, 'repair_price': 100}
```

## Using Forms to Determine Repair Service Cost

You can also calculate the repair service cost given the total amount and bike model cost using a modified form and instruction.

### Example Usage

The following code demonstrates how to find the repair service cost.

```python
form2 = BikeRepairInvoice(
    assignment="total_amount, bike_price -> repair_price",
    total_amount=300,
    bike_price=100,
)

instruction2 = """
given the total amount and cost of bike model, find the repair service cost, return as an int, 
hint: repair_service = amount - bike_model
"""

# Create a new branch and send the instruction along with the modified form
branch = li.Branch()
c = await branch.chat(instruction=instruction2, form=form2)

# Get the assistant's response content
branch.messages[-1].content
# Output: {'assistant_response': "\`\`\`json\n{'repair_price': 200.0}\n\`\`\`"}

# Convert the response to a dictionary for further inspection
c.to_dict()
# Output: {'ln_id': '53827f7f4b0603af543aa27bbcf6fc88', 'created': '2024-05-14T02:08:42.314650', 'metadata': {...}, 'repair_price': 200.0, 'total_amount': 300.0, 'bike_price': 100}
```

## Conclusion

In this tutorial, we extended the basic usage of the `Branch` class from the LionAGI framework by introducing how to work with structured outputs using forms. We covered defining enums and forms, using forms to calculate the total amount for a bike repair invoice, and determining the repair service cost. By understanding these functionalities, you can effectively manage structured data and perform calculations within your LionAGI-based systems.
