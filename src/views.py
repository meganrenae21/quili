import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import pathname2url
from rich.rule import Rule
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from . import console
from .models import Question, QuizSession
from .storage import Attachment
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from typing import List
from datetime import datetime

class RuleDisplay:
    def __init__(self, title: str, text: str):
        self.title = title
        self.text = text
    
    def printRule(self):
        rule = Rule(title=self.title)
        console.print(rule)
        console.print(self.text)

class ListColumns:
    def __init__(self, contents: List[str]):
        self.contents = contents
        self.columns = Columns(contents, equal=True, expand=True)

    def printList(self):
        console.print(self.columns)

class QuestionEntry:
    def __init__(self, question: Question, subject_name: str):
        self.question = question
        self.subject_name = subject_name.capitalize()
    
    def printEntry(self):
        srule = Rule(title=self.subject_name)
        console.print(srule)
        RuleDisplay("Question", self.question.text).printRule()
        RuleDisplay("Choices", "\n".join([f"- {c}" for c in self.question.choices])).printRule()
        RuleDisplay("Answer", self.question.answer).printRule()
        if self.question.attachment is not None:
            panel = Panel(f"[italic]{self.question.attachment}.pdf[/italic]")
            console.print(panel)

class PassageView:
    def __init__(self, passage: str):
        self.passage = passage
    
    def printPassage(self):
        panel = Panel(self.passage)
        console.print(panel)

class DisplayQuestion:
    def __init__(self, subject_name: str, question_text: str, selections: List[tuple[str]], number: int):
        self.subject_name = subject_name
        self.question_text = question_text
        self.selections = selections
        self.number = number

    def printQuestion(self):
        RuleDisplay(f"{self.subject_name} Question {self.number}", self.question_text).printRule()
        hr = Rule()
        console.print(hr)
        for s in self.selections:
            console.print(f"{s[0]}. {s[1]}")
        console.print(hr)

class CheckAnswer:
    def __init__(self, question: Question, selected: str, selections: List[tuple[str]]):
        self.question = question
        self.selected = selected
        self.is_correct = (selected == question.answer)
        self.selections = selections

    def display(self):
        RuleDisplay(f"Question ID {self.question.id}", self.question.text).printRule()
        hr = Rule()
        console.print(hr)
        i = 1
        for _, c in self.selections:
            if c == self.question.answer and c == self.selected:
                console.print(f"[bold green]{i}. {c}[/bold green]")
            elif c == self.question.answer and c != self.selected:
                console.print(f"[green]{i}. {c}[/green]")
            elif c != self.question.answer and c == self.selected:
                console.print(f"[red]{i}. {c}[/red]")
            else:
                console.print(f"{i}. {c}")
            i += 1
        if self.is_correct:
            crule = Rule(title="CORRECT!")
            console.print(crule)
        else:
            irule = Rule(title="Incorrect")
            console.print(irule)

class QuestionAnswer:
    def __init__(self, question: Question):
        self.question = question

    def printAnswer(self):
        RuleDisplay("Question", self.question.text).printRule()
        RuleDisplay("Answer", self.question.answer).printRule()

class ProgressChart:
    def __init__(self, subject_name: str, data: List):
        self.subject_name = subject_name
        self.data = data

    def displayChart(self):
        dates = self.data[0]
        vals = self.data[1]
        plt.subplot()
        plt.plot(dates, vals)
        plt.suptitle(f"{self.subject_name} Progress")
        plt.show()

class QuizSummary:
    def __init__(self, quiz: QuizSession):
        self.quiz = quiz

    def show(self):
        grid = Table.grid()
        grid.add_column()
        grid.add_column(justify="right")
        grid.add_row("[bold]Subject[/bold]", self.quiz.subject.name)
        grid.add_row("[bold]Start[/bold]", datetime.strftime(self.quiz.start_time, "%Y-%m-%d %H:%M:%S"))
        grid.add_row("[bold]End[/bold]", datetime.strftime(self.quiz.end_time, "%Y-%m-%d %H:%M:%S"))
        grid.add_row("[bold]Questions[/bold]", str(self.quiz.length))
        grid.add_row("[bold]Correct[/bold]", str(self.quiz.correct))
        rawscore = (self.quiz.correct / self.quiz.length) * 100
        score = f"{rawscore}%"
        grid.add_row("[bold]Score[/bold]", score)
        console.print(grid)

class AttachmentViewer():
    def __init__(self, attachment: Attachment):
        self.path = Path(attachment.path).resolve()
    
    def _file_url(self) -> str:
        return urljoin("file:", pathname2url(str(self.path)))
    
    def _open_system(self) -> bool:
        if sys.platform.startswith("win"):
            try:
                os.startfile(str(self.path))
                return True
            except OSError:
                return False
        if sys.platform == "darwin":
            try:
                subprocess.run(["open", str(self.path)], check=False)
                return True
            except Exception:
                return False
        try:
            subprocess.run(["xdg-open", str(self.path)], check=False)
            return True
        except FileNotFoundError:
            return False
        except Exception: 
            return False
    
    def view(self) -> bool:
        if not self.path.exists():
            return False
        
        if self._open_system():
            return True
        
        try: 
            webbrowser.open(self._file_url())
            return True
        except Exception:
            return False