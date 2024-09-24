
# LionAGI Forms Tutorial

## Introduction

Forms are a fundamental feature in the LionAGI framework. They allow you to structure input data and manage the process of filling and working with this data. This tutorial provides an introduction to using forms in LionAGI.

## Table of Contents

1. [Creating a Form](#creating-a-form)
2. [Working with Form Fields](#working-with-form-fields)
3. [Filling and Validating a Form](#filling-and-validating-a-form)
4. [Handling Form Constraints](#handling-form-constraints)
5. [Inspecting the Form Object](#inspecting-the-form-object)
6. [Conclusion](#conclusion)

## Creating a Form

A form in LionAGI is defined using the `li.Form` class. You specify the fields and their relationships using the `assignment` parameter.

### Example Usage

The following code demonstrates how to create a form with two input fields and one output field.

```python
import lionagi as li

form = li.Form(assignment="input1, input2 -> output")
```

## Working with Form Fields

Once a form is created, you can inspect its input fields and requested output fields.

### Example Usage

The following code demonstrates how to retrieve and display the input and output fields of a form.

```python
# Retrieve input fields
form.input_fields
# Output: ['input1', 'input2']

# Retrieve requested fields
form.request_fields
# Output: ['output']
```

## Filling and Validating a Form

You can fill the form with data and check its status to see if it is workable or filled.

### Example Usage

The following code demonstrates how to fill a form with values and check its status.

```python
# Check if the form is workable (all input fields filled)
form.workable
# Output: False

# Check if the form is filled (all fields, including output, are filled)
form.filled
# Output: False

# Display the current state of form fields
form.work_fields
# Output: {'input1': None, 'input2': None, 'output': None}

# Fill the form with input values
form.fill(input1=1, input2=2)

# Check if the form is now workable
form.workable
# Output: True

# The form is not yet completely filled as the output is missing
form.filled
# Output: False

# Fill the output field
form.fill(output=3)

# Now the form should be completely filled
form.filled
# Output: True

# The form is no longer workable as it is completely filled
form.workable
# Output: False
```

## Handling Form Constraints

A form can only be filled once. Attempting to fill a form again after it has been filled will raise an error.

### Example Usage

The following code demonstrates how to handle the constraint of filling a form only once.

```python
# Attempt to fill the form again
try:
    form.fill(input1=2, input2=3)
except Exception as e:
    print(e)
# Output: Form is filled, cannot be worked on again

# Display the final state of form fields
form.work_fields
# Output: {'input1': 1, 'input2': 2, 'output': 3}
```

## Inspecting the Form Object

You can convert the form object to a dictionary to inspect all its properties and current state.

### Example Usage

The following code demonstrates how to convert a form to a dictionary.

```python
# Convert the form to a dictionary
form.to_dict()
# Output: {'input1': 1, 'input2': 2, 'output': 3, 'assignment': 'input1, input2 -> output', ...}
```

## Conclusion

In this tutorial, we covered the basics of using forms in the LionAGI framework. You learned how to create a form, fill it with data, check its status, and handle constraints related to form filling. By understanding these functionalities, you can effectively manage structured data within your LionAGI-based systems.
