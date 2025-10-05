import json
import os
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
from config import subjects_dir, progress_dir, user_file, attachment_dir
from .models import Subject, Progress, Question
from typing import List

class SubjectFile:
    def __init__(self, subject_name: str):
        self.subject_name = subject_name
        self.filename = subject_name.replace(" ", "-").lower()
        self.subject: Subject = None

    def save(self):
        data = json.dumps(self.subject, default=lambda x: x.__dict__, indent=4)
        with open(os.path.join(subjects_dir, f"{self.filename}.json"), 'w') as f:
            f.write(data)

    def load(self):
        with open(os.path.join(subjects_dir, f"{self.filename}.json"), 'r') as f:
            data = json.load(f)
            self.subject = Subject(data['name'])
            for q in data['questions']:
                question = Question(q['text'], q['choices'], q['answer'])
                question.id = q['id']
                if q['attachment']:
                    question.attachment = q['attachment']
                if q['passage']:
                    question.passage = q['passage']
                self.subject.add_question(question)

class ProgressFile:
    def __init__(self, subject_name: str):
        self.subject_name = subject_name
        self.filename = subject_name.replace(" ", "-")
        self.progress = None

    def save(self):
        data = json.dumps(self.progress, default=lambda x: x.__dict__, indent=4)
        with open(os.path.join(progress_dir, f"{self.filename}.json"), 'w') as f:
            f.write(data)
    
    def load(self):
        with open(os.path.join(progress_dir, f"{self.filename}.json"), 'r') as f:
            data = json.load(f)
            self.progress = Progress(data['subject_name'], data['quizzes'])

class UserFile:
    def __init__(self):
        self.filename = user_file
        self.subjects: List[str] = []

    def save(self):
        data = json.dumps({"subjects": self.subjects}, indent = 4)
        with open(self.filename, 'w') as f:
            f.write(data)

    def load(self):
        with open(self.filename, 'r') as f:
            data = json.load(f)
            self.subjects = data['subjects']

class Attachment:
    def __init__(self, question: Question):
        self.path = os.path.join(attachment_dir, f"{question.attachment}.pdf")

    

