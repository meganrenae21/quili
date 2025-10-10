import os
import click
from rich.prompt import Prompt, IntPrompt
from . import subjects
from .views import ListColumns, QuestionEntry, DisplayQuestion, CheckAnswer, ProgressChart, QuestionAnswer, AttachmentViewer, QuizSummary, PassageView
from . import subjects
from .models import Question, QuizSession
from .storage import ProgressFile, Attachment
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
    session = Session(subject_name)
    subject = session.load_subject()
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
    session.sf.save()

@quili.command()
@click.argument('subject_name')
@click.option('--length', '-l', type=int, default=10)
def quiz(subject_name: str, length: int):
    """Take a quiz for the specified subject with the specified number of questions. Default is 10."""
    if subject_name not in subjects:
        click.UsageError("There is no subject {subject_name}.")
    session = Session(subject_name)
    subject = session.load_subject()
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
            cs = cq.prepare_selections()
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
            qs.answer_current(selected_answer)
            check = CheckAnswer(cq, selected_answer, cs)
            check.display()
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
    if subject_name not in subjects:
        click.UsageError("There is no subject {subject_name}.")
    session = Session(subject_name)
    progress = session.load_progress()
    data = progress.prepare_data()
    chart = ProgressChart(subject_name, data)
    chart.displayChart()

@quili.command
@click.argument('subject_name')
def listquestions(subject_name: str):
    """List all questions for a given subject with their corresponding IDs."""
    if subject_name not in subjects:
        click.UsageError("There is no subject {subject_name}.")
    session = Session(subject_name)
    subject = session.load_subject()
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
    if subject_name not in subjects:
        click.UsageError("There is no subject {subject_name}.")
    session = Session(subject_name)
    subject = session.load_subject()
    q = subject.get_question_by_id(question_id) 
    sels = q.prepare_selections()
    sel_strs = []
    for s in sels:
        sstr = f"{s[0]}. {s[1]}"
        sel_strs.append(sstr)
    cols = ListColumns(sel_strs)
    cols.printList()

@quili.command
@click.argument('subject_name', type=str)
@click.argument('question_id', type=int)
def showanswer(subject_name, question_id):
    """Display the answer to a question."""
    if subject_name not in subjects:
        click.UsageError("There is no subject {subject_name}.")
    session = Session(subject_name)
    subject = session.load_subject()
    q = subject.get_question_by_id(question_id) 
    v = QuestionAnswer(q)
    v.printAnswer()

@quili.command
@click.argument('subject_name', type=str)
@click.argument('question_id', type=int)
def deleteq(subject_name, question_id):
    """Delete a question according to the specified subject and id. For a list of questions with their IDs, use listquestions SUBJECTNAME"""
    if subject_name not in subjects:
        click.UsageError("There is no subject {subject_name}.")
    session = Session(subject_name)
    subject = session.load_subject()
    q = subject.get_question_by_id(question_id)
    sure = Prompt.ask("Are you sure? This cannot be undone. Enter 'delete' to continue, otherwise press enter.'")
    if sure.lower() == "delete":
        subject.questions.remove(q)
        session.sf.save()

@quili.command
@click.argument('subject_name', type=str)
@click.argument('question_id', type=int)
@click.argument('choice_i', type=int)
def deletech(subject_name, question_id, choice_i):
    """Delete a choice (incorrect choice) of the question specified by its ID. Specify the choice by its index. For a list of questions with their IDs, use listquestions SUBJECTNAME. For a list of choices with their indices, use listchoices SUBJECTNAME QUESTIONID."""
    if subject_name not in subjects:
        click.UsageError("There is no subject {subject_name}.")
    session = Session(subject_name)
    subject = session.load_subject()
    q = subject.get_question_by_id(question_id)
    sure = Prompt.ask("Are you sure? This cannot be undone. Enter 'delete' to continue, otherwise press enter.'")
    if sure.lower() == "delete":
        q.choices.remove(q.choices[choice_i])
        session.sf.save()


