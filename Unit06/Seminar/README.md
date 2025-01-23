
# Secure Software Development - Unit 6 Seminar Answers

This document provides answers to the questions from the Unit 6 Seminar activities.

---

## **Question 1: Running `styleLint.py`**

### **What happens when the code is run?**
When running `styleLint.py`, the code raises an `IndentationError` because the `if` and `else` statements are not properly indented. Python relies on indentation to define code blocks, and the lack of proper indentation causes the code to fail.

### **Can you modify this code for a more favorable outcome?**
Yes, the code can be modified to fix the indentation issue.

### **What amendments have you made to the code?**
The corrected version of `styleLint.py` is as follows:

```python
def factorial(n):
    """Return factorial of n."""
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

