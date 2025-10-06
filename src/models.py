from typing import List, Dict
import random, datetime

class Question:
    def __init__(self, text: str, choices: List[str] = [], answer: str = ""):
        self.id = 0
        self.text = text
        self.choices = choices
        self.answer = answer
        self.attachment = None
        self.passage = None

    def add_choice(self, choice: str):
        self.choices.append(choice)

    def add_attachment(self, attachment_name):
        self.attachment = attachment_name

    def add_passage(self, passage: str):
        self.passage = passage

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "choices": self.choices,
            "answer": self.answer,
            "attachment": self.attachment,
            "passage": self.passage
        }

class Subject:
    def __init__(self, name: str, counter: int = 0):
        self.name = name
        self.questions: List[Question] = []
        self.counter = counter

    def increment_counter(self):
        self.counter += 1

    def add_question(self, question: Question):
        self.increment_counter()
        question.id = self.counter
        self.questions.append(question)
    
    def get_question_by_id(self, qid: int):
        return [q for q in self.questions if q.id == qid][0]
    
    def to_dict(self):
        return {
            "name": self.name,
            "counter": self.counter,
            "questions": [q.to_dict() for q in self.questions]
        }
    

class QuizAnswer:
    def __init__(self, question: Question, given_answer: str, is_correct: bool):
        self.question_id = question.id
        self.question_text = question.text
        self.given_answer = given_answer
        self.is_correct = is_correct

class QuizSession:
    def __init__(self, subject: Subject, length: int = 10):
        self.subject = subject
        self.correct: int = 0
        self.length = length
        self.questions: List[Question] = random.sample(subject.questions, length)
        self.current: int = 0
        self.start_time = datetime.datetime.now()
        self.answers: List[QuizAnswer] = [] 
        self.end_time = None
    
    def prepare_question(self):
        q = self.questions[self.current]
        return q

    def prepare_selections(self, question: Question):
        mc = []
        for c in question.choices:
            mc.append(c)
        mc.append(question.answer)
        random.shuffle(mc)
        opts = []
        for i in range(1, len(mc) + 1):
            opts.append(i)
        selections = list(zip(opts, mc))
        return selections
    
    def answer_current(self, answer: str):
        question = self.questions[self.current]
        if question.answer == answer:
            self.correct += 1
            result = True
        else:
            result = False
        self.current += 1
        qa = QuizAnswer(question, answer, result)
        self.answers.append(qa)
        return result
    
    def is_finished(self) -> bool:
        return self.current == self.length
    
    def finish(self):
        self.end_time = datetime.datetime.now()


class Progress:
    def __init__(self, subject_name: str, quizzes: List[Dict] = []):
        self.subject_name = subject_name
        self.quizzes = quizzes

    def add_quiz(self, quiz: QuizSession):
        qz = {
            "id": len(self.quizzes) + 1,
            "answers": quiz.answers,
            "score": quiz.correct,
            "length": quiz.length,
            "start": quiz.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end": quiz.end_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.quizzes.append(qz)

    def prepare_data(self):
        dates = []
        scores = []
        for q in self.quizzes:
            d = datetime.datetime.strptime(q['end'],"%Y-%m-%d %H:%M:%S")
            dl = d.strftime("%x")
            dates.append(dl)
            s = q['score']/q['length'] * 100
            scores.append(s)
        return [dates, scores]
    
    def to_dict(self):
        return {
            "subject_name": self.subject_name,
            "quizzes": self.quizzes
        }
