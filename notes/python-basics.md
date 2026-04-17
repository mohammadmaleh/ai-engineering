# Python Basics

## Dicts

Key-value pairs. Like a JS object but accessed with brackets, not dots.

```python
user = {"name": "Mohamad", "age": 30}

user["name"]        # "Mohamad"
user.get("name")    # safer — returns None instead of crashing if key missing
```

- Use brackets: `user["name"]` ← not `user.name` (that's for classes)
- f-strings with dicts: `f"Hello {user['name']}"`

## Lists

Ordered collection. Like a JS array.

```python
items = ["apple", "banana", "cherry"]
items.append("date")   # add to end
items.pop()            # remove last
items[0]               # first
items[-1]              # last ← works in Python, not in JS
len(items)             # length
"apple" in items       # True
```

## For Loops

Like `for...of` in JS. Use `.items()` for dicts.

```python
# list
for item in items:
    print(item)

# dict
for key, value in user.items():
    print(key, value)
```

- No parentheses on `for`
- `.items()` = `Object.entries()`

## Functions

Like JS functions but `def` instead of `function`. No type annotations required.

```python
def greet(name):
    return f"Hello {name}"

result = greet("Mohamad")
print(result)

# default arguments
def greet(name, greeting="Hello"):
    return f"{greeting} {name}"

greet("Mohamad")          # "Hello Mohamad"
greet("Mohamad", "Hi")    # "Hi Mohamad"
```

## If / Elif / Else

```python
if age >= 18:
    print("adult")
elif age >= 13:
    print("teenager")
else:
    print("child")



- Check None with `is`: `if x is None:`
- Not None: `if x is not None:`
```

## Try / Except

Like `try/catch` in JS. Catches errors so the app doesn't crash.

```python
try:
    number = int("not a number")
except ValueError as e:
    print("Invalid number:", e)
except Exception as e:
    print("Something else went wrong:", e)
```

- `catch` → `except Exception as e`
- More specific exceptions first, `Exception` last as a catch-all

## List Comprehensions

Like `.map()` and `.filter()` in JS but in one line.

```python
numbers = [1, 2, 3, 4, 5]

# map equivalent
doubled = [n * 2 for n in numbers]       # [2, 4, 6, 8, 10]

# filter equivalent
evens = [n for n in numbers if n % 2 == 0]  # [2, 4]
```

- Pattern: `[expression for item in list]`
- With filter: `[expression for item in list if condition]`

## Async / Await

Like JS async/await. Lets the server handle other requests while waiting on I/O.

```python
# sync — blocks until done
def get_user():
    return db.query(User)

# async — pauses and lets other requests run while waiting
async def get_user():
    return await db.query(User)
```

- Use `async def` + `await` for anything that does I/O (database, HTTP, file)
- In FastAPI: all route handlers should be `async def`

## Decorators

A label that wraps a function and registers it. Like `app.get()` in Express but different syntax.

```python
@app.get("/users")
async def get_users():
    return []
```

- `@app.get`, `@app.post`, `@app.delete` — register FastAPI routes
- You won't write your own decorators, just use them

## imports

```python
import os # import whole module
from dotenv import load_dotenv # import specific function
from fastapi import FastAPI, HTTPException # import multiple
```

one thing that I will use constantly

```python
import os
os.getenv("DATABASE_URL") # get env variable
```
