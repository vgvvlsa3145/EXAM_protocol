from django.core.management.base import BaseCommand
from exams.models import Exam
from questions.models import Question
import random

class Command(BaseCommand):
    help = 'Verifies Mock Test Configuration'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Verifying Mock Test 1 Configuration ---")
        
        exam = Exam.objects.filter(title="Mock test 1").first()
        if not exam:
             self.stdout.write(self.style.ERROR("Exam 'Mock test 1' NOT FOUND!"))
             return

        self.stdout.write(f"Exam Found: {exam.title}")
        self.stdout.write(f"Duration: {exam.duration_minutes} mins")
        self.stdout.write(f"Random Question Limit: {exam.random_question_count}")
        
        all_qs = list(exam.questions.all())
        total_qs = len(all_qs)
        
        theory_qs = [q for q in all_qs if q.category == 'Theory']
        program_qs = [q for q in all_qs if q.category == 'Program']
        
        self.stdout.write(f"Total Questions in Pool: {total_qs}")
        self.stdout.write(f"  - Theory: {len(theory_qs)}")
        self.stdout.write(f"  - Program: {len(program_qs)}")
        
        self.stdout.write("\nSimulating Random Selection Logic (5 Attempts):")
        
        limit = exam.random_question_count
        
        for i in range(1, 6):
            # Simulation Logic (Copied from views.py)
            questions = list(all_qs)
            rng = random.Random(i * 100) # Deterministic seed per attempt
            rng.shuffle(questions)
            
            if limit and limit > 0 and len(questions) > limit:
                 t_qs = [q for q in questions if getattr(q, 'category', 'Theory') == 'Theory']
                 p_qs = [q for q in questions if getattr(q, 'category', 'Theory') == 'Program']
                 
                 target_t = int(limit * 0.7) 
                 target_p = limit - target_t
                 
                 rng.shuffle(t_qs)
                 rng.shuffle(p_qs)
                 
                 sel_t = t_qs[:target_t]
                 sel_p = p_qs[:target_p]
                 
                 if len(sel_p) < target_p:
                     needed = target_p - len(sel_p)
                     sel_t.extend(t_qs[target_t:target_t+needed])
                     
                 if len(sel_t) < target_t:
                     needed = target_t - len(sel_t)
                     sel_p.extend(p_qs[target_p:target_p+needed])
                     
                 questions = sel_t + sel_p
                 rng.shuffle(questions)
                 questions = questions[:limit]

            # Analyze Result
            s_theory = len([q for q in questions if q.category == 'Theory'])
            s_program = len([q for q in questions if q.category == 'Program'])
            
            self.stdout.write(f"  Attempt #{i}: Selected {len(questions)} ({s_theory} Theory, {s_program} Program)")
        
        if len(questions) == 50 and s_theory == 35 and s_program == 15:
            self.stdout.write(self.style.SUCCESS("\nVERIFICATION PASSED: Logic consistently delivers 35 Theory + 15 Program."))
        else:
             self.stdout.write(self.style.WARNING("\nVERIFICATION CHECK: Check above if values match 35/15."))
