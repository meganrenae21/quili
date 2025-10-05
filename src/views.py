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
        qrule = Rule(title="Question")
        console.print(qrule)
        console.print(self.question.text)
        crule = Rule(title="Choices")
        console.print(crule)
        for ch in self.question.choices:
            console.print(f"-  {ch}\n")
        arule = Rule(title="Answer")
        console.print(arule)
        console.print(self.question.answer)
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
        srule = Rule(title=f"{self.subject_name} Question {self.number}")
        console.print(srule)
        console.print(self.question_text)
        hr = Rule()
        console.print(hr)
        for s in self.selections:
            console.print(f"{s[0]}. {s[1]}")
        console.print(hr)

class CorrectAnswer:
    def __init__(self, subject_name: str, question_text: str, answer: str, selections: List[tuple[str]], number: int):
        self.subject_name = subject_name
        self.question_text = question_text
        self.answer = answer
        self.selections = selections
        self.number = number

    def printCorrect(self):
        srule = Rule(title=f"{self.subject_name} Question {self.number}")
        console.print(srule)
        console.print(self.question_text)
        hr = Rule()
        console.print(hr)
        for s in self.selections:
            if s[1] == self.answer:
                console.print(f"[bold green]{s[0]}. {s[1]}[/bold green]")
            else:
                console.print(f"{s[0]}. {s[1]}")
        crule = Rule(title="CORRECT!")
        console.print(crule)

class IncorrectAnswer:
    def __init__(self, subject_name: str, question_text: str, correct_answer: str, selected_answer: str, selections: List[tuple[str]], number: int):
        self.subject_name = subject_name
        self.question_text = question_text
        self.correct_answer = correct_answer
        self.selected_answer = selected_answer
        self.selections = selections
        self.number = number
    
    def printIncorrect(self):
        srule = Rule(title=f"{self.subject_name} Question {self.number}")
        console.print(srule)
        console.print(self.question_text)
        hr = Rule()
        console.print(hr)
        for s in self.selections:
            if s[1] == self.correct_answer:
                console.print(f"[green]{s[0]}. {s[1]}[/green]")
            elif s[1] == self.selected_answer:
                console.print(f"[red]{s[0]}. {s[1]}[/red]")
            else:
                console.print(f"{s[0]}. {s[1]}")
        irule = Rule(title="Incorrect")
        console.print(irule)

class QuestionAnswer:
    def __init__(self, question: Question):
        self.question = question

    def printAnswer(self):
        q = self.question.text
        a = self.question.answer
        qrule = Rule(title="Question")
        console.print(qrule)
        console.print(q)
        arule = Rule(title="Answer")
        console.print(arule)
        console.print(a)


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