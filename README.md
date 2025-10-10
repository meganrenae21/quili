# QuiLI
A command line application to create and take quizzes and track your progress across multiple subjects.

## Installation

Download and extract the latest [distribution](https://github.com/meganrenae21/quili/releases) or

```
git clone https://github.com/meganrenae21/quili.git
```

Then, from the root directory:

```
pip install .
```


## How it works

Each subject or class (or any other category) will have its own `[subject].json` file in the `data/subjects/` directory. This file will store every question added for that subject. 

Then, when you take a quiz for a subject, a random sample of questions will be pulled based on the length you specify. The number of questions you get right is divided against the number of questions in the quiz to give your score as a percentage. Each time you quiz yourself in a subject, your progress is measured against previous quizzes (and you can see your progress in a nifty little line chart). 

## Commands

### `quili add [subject-name]`

This will add a new subject to your subject list (stored in the `data/user.json` file) and create a new subject file at `data/subjects/[subject-name].json`. 

### `quili listsubs`

This will display a list of all subjects.

### `quili addq [subject-name]`

Creates a new question in `subject-name`. This command will prompt you to enter the question attributes:

- **Text**: The actual text of the question (*required*)
- **Passage**: A paragraph providing context to the question (*optional*)
- **Attachment**: The filename (without the extension) to a .pdf file in the `attachments/` directory. If provided, the file must exist. (*optional*)
- **Choices**: A list of *incorrect* choices. At least 3 are recommended. (*required*)
- **Answer**: The correct answer to the question. (*required*)

### `quili quiz [subject-name] [length]`

Begins a quiz in the terminal for `subject-name` with `length` questions. `length` must be an integer, and it must not be greater than the number of questions saved for `subject-name`.

### `quili progress [subject-name]`

Opens a line graph showing your scores over time for a given subject. Uses `matplotlib` and `PyQt5`. 

### `quili listquestions [subject-name]`

Lists all questions for `subject-name` as well as their IDs. 

### `quili listchoies [subject-name] [question-id]`

Lists the *incorrect* choices for `subject-name` question `question-id` as well as their indices. To get the id of a particular question, see `quili listquestions [subject-name]`. Note, `listchoices` does not show the answer. 

### `quili showanswer [subject-name] [question-id]`

Displays the question and answer for `subject-name` question `question-id`. 

### `quili deleteq [subject-name] [question-id]`

Deletes `subject-name` question `question-id`.

### `quili deletech [subject-name] [question-id] [choice-i]`

Deletes the choice at index `choice-i` for `subject-name` question `question-id`. 

## Included Subjects

- ACT Math: 10 questions of math questions from actual ACT and SAT exams and practice exams.
