import os
import click
from rich.prompt import Prompt, IntPrompt
from . import subjects
from .views import ListColumns, QuestionEntry, DisplayQuestion, CorrectAnswer, IncorrectAnswer, ProgressChart, QuestionAnswer, AttachmentViewer, QuizSummary, PassageView
from . import subjects
from .models import Question, QuizSession
from .storage import SubjectFile, ProgressFile, Attachment
from .session import Session
from config import attachment_dir

@click.group()
def quili():
    """CLI for QuiLI."""
    pass

@quili.command()
@click.argument('subject_name')
def add(subject_name: str):
    """Add a new subject."""
    if subject_name in subjects:
        raise ValueError(f"Subject {subject_name} already exists.")
    else:
        session = Session(subject_name)
        session.add_subject(subject_name)
        click.echo(f"Subject {subject_name} added.")


@quili.command()
def listsubs():
    """List all existing subjects."""
    cols = ListColumns(subjects)
    cols.printList()

@quili.command()
@click.argument('subject_name')
def addq(subject_name: str):
    """Add a question to a subject. Gives prompts for question text, choices, and answer. If the subject does not exist, it will be created."""
    sf = SubjectFile(subject_name)
    sf.load()
    subject = sf.subject
    q = Prompt.ask("Enter question text.")
    question = Question(q)
    passage = Prompt.ask("If there is a reading passage to go with this question, please enter it here. Otherwise, enter 'none'.")
    if passage.lower() != "none":
        question.add_passage(passage)
    attach = Prompt.ask("Enter the filename of attachmentfor this question, or enter 'none' if no attachment.")
    if attach.lower() != "none":
        if f"{attach}.pdf" not in os.listdir(attachment_dir):
            return FileNotFoundError(f"No attachment file found named ${attach}.pdf in attachment directory.")
        else:
            question.add_attachment(attach)
    while True:
        choice = Prompt.ask("Enter an INCORRECT choice. Enter done when finished.")
        if choice.lower() == "done": 
            break
        question.add_choice(choice)
    a = Prompt.ask("Enter the CORRECT answer.")
    question.answer = a
    subject.add_question(question)
    entry = QuestionEntry(question, subject_name)
    entry.printEntry()
    sf.save()

@quili.command()
@click.argument('subject_name')
@click.option('--length', '-l', type=int, default=10)
def quiz(subject_name: str, length: int):
    """Take a quiz for the specified subject with the specified number of questions. Default is 10."""
    sf = SubjectFile(subject_name)
    sf.load()
    subject = sf.subject
    if len(subject.questions) < length:
        raise ValueError(f"Not enough questions in subject {subject_name} for quiz length {length}.")
    else:
        qs = QuizSession(subject, length)
        while not qs.is_finished():
            c = qs.current
            cq = qs.prepare_question()
            if cq.passage is not None:
                pv = PassageView(cq.passage)
                pv.printPassage()
            cs = qs.prepare_selections(cq)
            dq = DisplayQuestion(subject.name, cq.text, cs, c)
            dq.printQuestion()
            if cq.attachment is not None:
                attachment = Attachment(cq)
                viewer = AttachmentViewer(attachment)
                viewer.view()
            sel = IntPrompt.ask("Enter the NUMBER of your answer among the options above.")
            ind = sel - 1
            selected_tuple = cs[ind]
            selected_answer = selected_tuple[1]
            correct = qs.answer_current(selected_answer)
            if correct:
                display = CorrectAnswer(subject_name, cq.text, cq.answer, cs, c)
                display.printCorrect()
            else:
                display = IncorrectAnswer(subject_name, cq.text, cq.answer, selected_answer, cs, c)
                display.printIncorrect()
            confirm = Prompt.ask("Press any key to continue.")
            if confirm:
                continue
        qs.finish()
        session = Session(subject_name)
        progress = session.load_progress()
        progress.add_quiz(qs)
        pfile = ProgressFile(subject_name)
        pfile.progress = progress
        pfile.save()
        summary = QuizSummary(qs)
        summary.show()

@quili.command
@click.argument('subject_name')
def progress(subject_name: str):
    """Display a graph showing your scores through time in a specified subject."""
    session = Session(subject_name)
    progress = session.load_progress()
    data = progress.prepare_data()
    chart = ProgressChart(subject_name, data)
    chart.displayChart()

@quili.command
@click.argument('subject_name')
def listquestions(subject_name: str):
    """List all questions for a given subject with their corresponding IDs."""
    sf = SubjectFile(subject_name)
    sf.load()
    subject = sf.subject
    strs = []
    for question in subject.questions:
        s = f"{question.id} {question.text}"
        strs.append(s)
    cols = ListColumns(strs)
    cols.printList()

@quili.command
@click.argument('subject_name', type=str)
@click.argument('question_id', type=int)
def listchoices(subject_name, question_id):
    """Displays a list of all the incorrect choices for a given question. Does not display the answer."""
    sf = SubjectFile(subject_name)
    sf.load()
    subject = sf.subject
    questions = subject.questions
    q = [qu for qu in questions if qu.id == question_id][0]
    chs = []
    for val in range(len(q.choices)):
        ch = f"{val} {q.choices[val]}"
        chs.append(ch)
    cols = ListColumns(chs)
    cols.printList()

@quili.command
@click.argument('subject_name', type=str)
@click.argument('question_id', type=int)
def showanswer(subject_name, question_id):
    """Display the answer to a question."""
    sf = SubjectFile(subject_name)
    sf.load()
    subject = sf.subject
    questions = subject.questions
    q = [qu for qu in questions if qu.id == question_id][0]
    v = QuestionAnswer(q)
    v.printAnswer()

@quili.command
@click.argument('subject_name', type=str)
@click.argument('question_id', type=int)
def deleteq(subject_name, question_id):
    """Delete a question according to the specified subject and id. For a list of questions with their IDs, use listquestions SUBJECTNAME"""
    sf = SubjectFile(subject_name)
    sf.load()
    subject = sf.subject
    questions = subject.questions
    q = [qu for qu in questions if qu.id == question_id][0]
    sure = Prompt.ask("Are you sure? This cannot be undone. Enter 'delete' to continue, otherwise press enter.'")
    if sure.lower() == "delete":
        subject.questions.remove(q)
        sf.save()

@quili.command
@click.argument('subject_name', type=str)
@click.argument('question_id', type=int)
@click.argument('choice_i', type=int)
def deletech(subject_name, question_id, choice_i):
    """Delete a choice (incorrect choice) of the question specified by its ID. Specify the choice by its index. For a list of questions with their IDs, use listquestions SUBJECTNAME. For a list of choices with their indices, use listchoices SUBJECTNAME QUESTIONID."""
    sf = SubjectFile(subject_name)
    sf.load()
    subject = sf.subject
    questions = subject.questions
    q = [qu for qu in questions if qu.id == question_id][0]
    sure = Prompt.ask("Are you sure? This cannot be undone. Enter 'delete' to continue, otherwise press enter.'")
    if sure.lower() == "delete":
        q.choices.remove(q.choices[choice_i])
        sf.save()


