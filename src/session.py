from .models import Subject, Progress
from .storage import SubjectFile, ProgressFile
from . import subjects, uf

class Session:
    def __init__(self, subject_name: str):
        self.subject_name = subject_name
        self.sf = SubjectFile(subject_name)

    def load_subject(self) -> Subject:
        if self.subject_name in subjects:
            self.sf.load()
            return self.sf.subject
        else:
            return self.add_subject(self.subject_name)

    def add_subject(self, subject_name):
        new_subject = Subject(subject_name)
        subjects.append(subject_name)
        uf.save()
        sf = SubjectFile(subject_name)
        sf.subject = new_subject
        sf.save()
        return new_subject

    def load_progress(self):
        pfile = ProgressFile(self.subject_name)
        try:
            pfile.load()
            return pfile.progress
        except FileNotFoundError:
            return self.add_progress(pfile)
        
    def add_progress(self, pfile: ProgressFile):
        new_progress = Progress(self.subject_name)
        pfile.progress = new_progress
        pfile.save()
        return new_progress
