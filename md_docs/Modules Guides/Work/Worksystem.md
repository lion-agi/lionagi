
# LionAGI Work System Tutorial

## Introduction

In this tutorial, we will explore the work system in LionAGI, focusing on how to define and utilize workers to handle tasks asynchronously. We will demonstrate this by creating a custom worker that processes chat instructions, adding tasks to the worker's worklog, processing these tasks, and viewing the results.

## Table of Contents

1. [Setup](#setup)
2. [Creating a Custom Worker](#creating-a-custom-worker)
3. [Adding Tasks to the Worker](#adding-tasks-to-the-worker)
4. [Processing Tasks](#processing-tasks)
5. [Viewing the Results](#viewing-the-results)
6. [Conclusion](#conclusion)

## Setup

First, let's import the necessary library.

```python
import lionagi as li
```

## Creating a Custom Worker

We define a custom worker class `Coder` that inherits from `li.Worker`. The worker is designed to handle chat instructions with specified capacity, timeout, and refresh time.

```python
class Coder(li.Worker):
    name = "coder"

    @li.work(capacity=5, timeout=5, refresh_time=1)
    async def chat(self, instruction=None, context=None):
        branch = li.Branch()
        return await branch.chat(instruction=instruction, context=context)
```

Instantiate the `Coder` worker.

```python
coder = Coder()
```

## Adding Tasks to the Worker

We will add multiple chat tasks to the worker's worklog. Each task involves providing an instruction and context for the chat function.

```python
# Calling the function only adds it to the internal worklog
instruction = (
    "write a serious hello world according to the given language, answer only in emoji"
)
languages = ["python", "c++", "java", "javascript", "ruby", "php", "c#", "matlab"]

for i in languages:
    await coder.chat(instruction=instruction, context=i)
```

## Checking the Worklog

We can inspect the worker's worklog to see the added tasks and their status.

```python
chat_func_log = coder.work_functions["chat"].worklog

print("Total number of work items in the worklog: \t\t", len(chat_func_log.pile))
print("Total number of pending items in the worklog: \t\t", len(chat_func_log.pending))
print(
    "Available capacity remaining in the async queue: \t",
    chat_func_log.queue.available_capacity,
)
```

## Processing Tasks

The `forward` and `process` methods are used to process the tasks in the worklog.

```python
await chat_func_log.forward()
await chat_func_log.queue.process()
```

## Viewing the Results

Once the tasks are processed, we can view the results for each task.

```python
for language, work in zip(languages, chat_func_log.completed_work.values()):
    print(f"{language}: {work.result}")
```

### Example Output

python: 🐍💻🖥️:
```python
print("Hello, World!")
```

c++:
```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "🌍👋" << endl;
    return 0;
}
```

java:
```java
👋🌍🛠️☕💻
```

javascript:
```javascript
console.log("👋🌍");
```

ruby:
```ruby
👋🌍
```

php:
```php
<?php
echo "👋🌍";
?>
```

c#:
```
👋🌍
```

matlab:
```matlab
disp('👋🌍')
```

We can also convert the worklog into a dataframe to view the detailed status of each task.

```python
chat_func_log.pile.to_df()
```

### Example DataFrame Output

```markdown
                              ln_id                     created  \
0  1d83d5869bda3cd48d71b4e1bcc20d8c  2024-05-14T02:08:47.770981
1  1eee56b3cfa52375e4a87efb530582c6  2024-05-14T02:08:47.771030
2  d36e13084a824a2e4e880c726d2c8799  2024-05-14T02:08:47.771046
3  3ddc0be116f799288e0a107f5df4163e  2024-05-14T02:08:47.771061
4  a1100aa0df9209fc400164cb580371b1  2024-05-14T02:08:47.771073
5  30d22e8c32d20a7cf65e09db4c7fe052  2024-05-14T02:08:47.771084
6  8a928c0d06b9fab9e2f812f9f15a948b  2024-05-14T02:08:47.771095
7  2f875d1fa6b76c82d399610bf17aa80b  2024-05-14T02:08:47.771110

                                            metadata content  \
0  {'last_updated': {'status': '2024-05-14T02:08:...    None
1  {'last_updated': {'status': '2024-05-14T02:08:...    None
2  {'last_updated': {'status': '2024-05-14T02:08:...    None
3  {'last_updated': {'status': '2024-05-14T02:08:...    None
4  {'last_updated': {'status': '2024-05-14T02:08:...    None
5  {'last_updated': {'status': '2024-05-14T02:08:...    None
6  {'last_updated': {'status': '2024-05-14T02:08:...    None
7  {'last_updated': {'status': '2024-05-14T02:08:...    None

                 status                                             result  \
0  WorkStatus.COMPLETED      🐍💻🖥️:\n\`\`\`python\nprint("Hello, World!")\n\`\`\`
1  WorkStatus.COMPLETED  \`\`\`cpp\n#include <iostream>\nusing namespace s...
2  WorkStatus.COMPLETED                                    \`\`\`java\n👋🌍🛠️☕💻
3  WorkStatus.COMPLETED             \`\`\`javascript\nconsole.log("👋🌍");\n\`\`\`
4  WorkStatus.COMPLETED                                   \`\`\`ruby\n👋🌍\n\`\`\`
5  WorkStatus.COMPLETED                 \`\`\`\php\n<?php\necho "👋🌍";\n?>\n\`\`\`
6  WorkStatus.COMPLETED                                       \`\`\`\n👋🌍\n\`\`\`
7  WorkStatus.COMPLETED                         \`\`\`matlab\ndisp('👋🌍')\n\`\`\`

  error        completion_timestamp  duration
0  None  2024-05-14T02:08:48.866292  1.095071
1  None  2024-05-14T02:08:48.866428  1.009315
2  None  2024-05-14T02:08:48.866513  0.739154
3  None  2024-05-14T02:08:48.866595  0.670039
4  None  2024-05-14T02:08:48.866680  0.652948
5  None  2024-05-14T02:08:48.875319  0.726192
6  None  2024-05-14T02:08:48.875526  0.595971
7  None  2024-05-14T02:08:48.875733  0.691921
```

## Conclusion

In this tutorial, we covered the fundamentals of LionAGI's work system, including creating custom workers, adding tasks, processing them, and viewing the results. This system allows for efficient and structured task management, enabling asynchronous processing of multiple tasks with ease.
