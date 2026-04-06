from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Exam, StudentExamAttempt
from security.middleware import IPRestrictionMiddleware
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@login_required
def student_dashboard(request):
    if not request.user.is_student():
        return redirect('dashboard')
        
    # Get active exams
    now = timezone.now()
    active_exams_qs = Exam.objects.filter(start_time__lte=now, end_time__gt=now, is_active=True)
    
    # Exclude submitted exams
    submitted_exam_ids = StudentExamAttempt.objects.filter(
        student=request.user, 
        status='SUBMITTED'
    ).values_list('exam_id', flat=True)
    
    active_exams = active_exams_qs.exclude(id__in=submitted_exam_ids)
    upcoming_exams = Exam.objects.filter(start_time__gt=now, is_active=True)
    past_attempts = StudentExamAttempt.objects.filter(student=request.user)
    
    today = timezone.localtime(timezone.now())
    current_hour = today.hour
    
    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    # Identify exams that are in progress
    in_progress_exams = set(StudentExamAttempt.objects.filter(
        student=request.user, 
        status='IN_PROGRESS',
        exam__in=active_exams
    ).values_list('exam_id', flat=True))

    return render(request, 'exams/student_dashboard.html', {
        'active_exams': active_exams,
        'upcoming_exams': upcoming_exams,
        'past_attempts': past_attempts,
        'greeting': greeting,
        'in_progress_ids': in_progress_exams
    })

@login_required
def exam_instructions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Validation: Has student already submitted?
    attempt = StudentExamAttempt.objects.filter(student=request.user, exam=exam).first()
    if attempt and attempt.status == 'SUBMITTED':
        return redirect('student_dashboard')
        
    return render(request, 'exams/instructions.html', {'exam': exam})

@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Validation constraints
    if not request.user.is_student():
        return redirect('dashboard')
        
    now = timezone.now()
    if now < exam.start_time or now > exam.end_time:
        return render(request, 'exams/exam_error.html', {'message': 'This exam is not currently active.'})
        
    # Check if already attempted
    attempt, created = StudentExamAttempt.objects.get_or_create(
        student=request.user, 
        exam=exam
    )
    
    if attempt.status == 'SUBMITTED':
        return render(request, 'exams/exam_error.html', {'message': 'You have already submitted this exam.'})
    
    # Check IP binding if created (Logic: 1 IP per session)
    # We can update the attempt with the current IP
    client_ip = IPRestrictionMiddleware(None).get_client_ip(request)
    if not attempt.ip_address:
        attempt.ip_address = client_ip
        attempt.save()
    elif attempt.ip_address != client_ip:
         # Optional: Strict Mode - Block if IP changes (anti-cheat)
         # For now, we log it or warn.
         pass 

    # Audit Log
    from security.models import AuditLog
    AuditLog.objects.create(
        user=request.user,
        action="Exam Started",
        ip_address=client_ip,
        details=f"Started exam: {exam.title}"
    )

    # Calculate remaining time
    # If resuming, time = (Attempt Start + Duration) - Now
    import datetime
    import random
    
    exam_duration_sec = exam.duration_minutes * 60
    
    # Check if we should enforce strict time window (Exam End Time)
    # Remaining time based on absolute exam end time
    time_to_exam_end = (exam.end_time - now).total_seconds()
    
    elapsed = (now - attempt.start_time).total_seconds()
    remaining_seconds = max(0, exam_duration_sec - elapsed)
    
    # Also clamp to exam hard end time
    remaining_seconds = min(remaining_seconds, time_to_exam_end)
    
    # If time is up, auto-submit
    if remaining_seconds <= 0:
        return redirect('submit_exam', exam_id=exam.id)

    # Randomize Questions and Options (Deterministic per Attempt)
    # We use the attempt.id as a seed so the order persists on refresh for the same user
    questions = list(exam.questions.all())
    rng = random.Random(attempt.id)
    rng.shuffle(questions)
    
    # NEW FEATURE: Random Subset (e.g. 50 out of 150)
    # NEW FEATURE: Random Subset with Category Logic (Aim for 70% Theory, 30% Program)
    limit = exam.random_question_count
    if limit and limit > 0 and len(questions) > limit:
         theory_qs = [q for q in questions if getattr(q, 'category', 'Theory') == 'Theory']
         program_qs = [q for q in questions if getattr(q, 'category', 'Theory') == 'Program']
         
         # Target counts (Use model fields if set, otherwise default to 70/30)
         if exam.theory_count is not None and exam.program_count is not None:
             target_theory = exam.theory_count
             target_program = exam.program_count
         else:
             target_theory = int(limit * 0.7) # Default 35 for 50
             target_program = limit - target_theory # Default 15 for 50
         
         # Shuffle pools
         rng.shuffle(theory_qs)
         rng.shuffle(program_qs)
         
         # Select (Fill logic: if not enough program, take more theory, and vice versa)
         selected_theory = theory_qs[:target_theory]
         selected_program = program_qs[:target_program]
         
         # If we are short on program, fill with theory
         if len(selected_program) < target_program:
             needed = target_program - len(selected_program)
             extra_theory = theory_qs[target_theory:target_theory+needed]
             selected_theory.extend(extra_theory)
             
         # If we are short on theory (unlikely), fill with program
         if len(selected_theory) < target_theory:
             needed = target_theory - len(selected_theory)
             extra_program = program_qs[target_program:target_program+needed]
             selected_program.extend(extra_program)
             
         questions = selected_theory + selected_program
         # Shuffle final combined list
         rng.shuffle(questions)
         # Ensure strict limit just in case
         questions = questions[:limit]
    
    # Shuffle options for each question
    for q in questions:
        q.shuffled_options = list(q.options.all())
        rng_opts = random.Random(attempt.id + q.id)
        rng_opts.shuffle(q.shuffled_options)
    
    # Pre-fetch existing answers for Resume functionality
    from results.models import StudentAnswer
    saved_answers_qs = StudentAnswer.objects.filter(attempt=attempt)
    saved_answers = {}
    for ans in saved_answers_qs:
        if ans.question.question_type == 'MCQ' and ans.selected_option:
            saved_answers[ans.question.id] = ans.selected_option.id
        else:
            saved_answers[ans.question.id] = ans.text_answer

    # Attach saved answer to each question object for easy template access
    for q in questions:
        # We use a default of None. Ensure types match (int vs int)
        val = saved_answers.get(q.id)
        # For MCQ, val is option ID (int/long).
        # For Subjective, val is string.
        q.user_answer = val

    return render(request, 'exams/take_exam.html', {
        'exam': exam,
        'questions': questions,
        'attempt': attempt,
        'duration_seconds': int(remaining_seconds),
        'saved_answers': saved_answers
    })

@login_required
@csrf_exempt
def submit_exam(request, exam_id):
    if request.method != 'POST':
        return redirect('take_exam', exam_id=exam_id)
        
    exam = get_object_or_404(Exam, id=exam_id)
    attempt = get_object_or_404(StudentExamAttempt, student=request.user, exam=exam)
    
    if attempt.status == 'SUBMITTED':
         return redirect('student_dashboard')

    # SECURITY PATCH 1: Check Deadline
    from django.utils import timezone
    from django.contrib import messages
    now = timezone.now()
    
    # Half-time minimum stay logic has been removed.

    if now > exam.end_time:
        # If past deadline, we still allow submission but maybe log it or flag it?
        # Actually, standard procedure is to block it if it's way past.
        # Let's allow a 30-second "grace period" for network lag.
        if (now - exam.end_time).total_seconds() > 60:
             attempt.status = 'SUBMITTED' # Force close
             attempt.save()
             messages.error(request, "Submission rejected: Exam time has expired.")
             return redirect('student_dashboard')

    # Process Answers
    from results.models import StudentAnswer
    from questions.models import Question, Option
    
    score = 0
    
    for key, value in request.POST.items():
        if key.startswith('question_'):
            q_id = key.split('_')[1]
            try:
                question = Question.objects.get(id=q_id)
                
                # SECURITY PATCH 2: Validate option belongs to question
                if question.question_type == 'MCQ':
                    selected_opt_id = value
                    try:
                        selected_opt = Option.objects.get(id=selected_opt_id)
                        # Ensure this option belongs to THIS question
                        if selected_opt.question_id != int(q_id):
                             continue # Skip malicious/invalid input
                    except Option.DoesNotExist:
                        continue
                
                # Create or Update Answer Record (Safely handling duplicates)
                ans = StudentAnswer.objects.filter(attempt=attempt, question=question).first()
                if not ans:
                    ans = StudentAnswer(attempt=attempt, question=question)
                
                if question.question_type == 'MCQ':
                    ans.selected_option = selected_opt
                    if selected_opt.is_correct:
                        ans.marks_awarded = question.marks
                        score += question.marks
                    else:
                        ans.marks_awarded = 0
                else:
                    ans.text_answer = value
                
                ans.save()
            except Question.DoesNotExist:
                continue
            
    attempt.score = score
    attempt.status = 'SUBMITTED'
    attempt.submit_time = now
    attempt.save()
    
    return redirect('student_dashboard')

@login_required
def reset_attempt(request, attempt_id):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    
    # Audit Log
    from security.models import AuditLog
    # Helper to get IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    AuditLog.objects.create(
        user=request.user,
        action="Reset Exam",
        ip_address=ip,
        details=f"Reset/Deleted exam attempt for student '{attempt.student.username}' in exam '{attempt.exam.title}'"
    )
    
    attempt.delete() 
    return redirect('admin_dashboard')

@login_required
def publish_results(request, exam_id):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
    
    exam = get_object_or_404(Exam, id=exam_id)
    exam.results_published = not exam.results_published # Toggle
    exam.save()
    
    status = "Published" if exam.results_published else "Hidden"
    # Log it
    from security.models import AuditLog
    AuditLog.objects.create(
        user=request.user,
        action="Results Update",
        details=f"Results for '{exam.title}' are now {status}"
    )
    
    return redirect('admin_dashboard')

@login_required
def export_results_csv(request, exam_id):
    import csv
    from django.http import HttpResponse
    
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    exam = get_object_or_404(Exam, id=exam_id)
    attempts = StudentExamAttempt.objects.filter(exam=exam, status='SUBMITTED')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{exam.title}_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student Username', 'Roll Number', 'Score', 'Total Marks', 'Date Submitted'])
    
    for attempt in attempts:
        roll = getattr(attempt.student.studentprofile, 'roll_number', 'N/A') if hasattr(attempt.student, 'studentprofile') else 'N/A'
        writer.writerow([
            attempt.student.username, 
            roll, 
            attempt.score, 
            exam.total_marks, 
            attempt.submit_time
        ])
        
    return response

@login_required
def view_result(request, attempt_id):
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    
    # Security: Only the student who took it (or admin) can see it
    if request.user != attempt.student and not request.user.is_staff and request.user.role not in ['ADMIN', 'FACULTY']:
        return redirect('dashboard')
        
    # Security: Results must be published
    if not attempt.exam.results_published and not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('student_dashboard')
        
    # Fetch answers
    from results.models import StudentAnswer
    student_answers = StudentAnswer.objects.filter(attempt=attempt).select_related('question', 'selected_option')
    
    return render(request, 'exams/view_result.html', {
        'attempt': attempt,
        'exam': attempt.exam,
        'student_answers': student_answers
    }) 

@login_required
@csrf_exempt
def autosave_exam(request, exam_id):
    if request.method != 'POST':
        from django.http import JsonResponse
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)
        
    exam = get_object_or_404(Exam, id=exam_id)
    attempt = StudentExamAttempt.objects.filter(student=request.user, exam=exam, status='IN_PROGRESS').first()
    
    if not attempt:
         from django.http import JsonResponse
         return JsonResponse({'status': 'error', 'message': 'No active attempt found'}, status=404)

    # Process Answers from POST data
    from results.models import StudentAnswer
    from questions.models import Question, Option
    import json

    data = request.POST # Default form data
    
    # If using fetch body: JSON.stringify
    if not data and request.body:
        try:
            data = json.loads(request.body)
        except:
            pass

    saved_count = 0
    
    for key, value in data.items():
        if key.startswith('question_'):
            q_id = key.split('_')[1]
            try:
                question = Question.objects.get(id=q_id)
                
                # Save Answer safely
                ans = StudentAnswer.objects.filter(
                    attempt=attempt,
                    question=question
                ).first()
                
                if not ans:
                    ans = StudentAnswer.objects.create(
                        attempt=attempt,
                        question=question
                    )
                
                if question.question_type == 'MCQ':
                    selected_opt_id = value
                    try:
                        selected_opt = Option.objects.get(id=selected_opt_id)
                        ans.selected_option = selected_opt
                        
                        if selected_opt.is_correct:
                            ans.marks_awarded = question.marks
                        else:
                            ans.marks_awarded = 0
                    except Option.DoesNotExist:
                        pass
                else:
                    ans.text_answer = value
                
                ans.save()
                saved_count += 1
            except Question.DoesNotExist:
                continue

    from django.http import JsonResponse
    return JsonResponse({'status': 'success', 'saved': saved_count})

@login_required
def force_submit_attempt(request, attempt_id):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    
    if attempt.status == 'SUBMITTED':
        from django.contrib import messages
        messages.info(request, "This exam is already submitted.")
        return redirect('admin_dashboard')

    # Calculate Score based on Saved Answers (Auto-Save)
    from results.models import StudentAnswer
    saved_answers = StudentAnswer.objects.filter(attempt=attempt)
    
    score = 0
    for ans in saved_answers:
        if ans.question.question_type == 'MCQ' and ans.selected_option:
            if ans.selected_option.is_correct:
                 ans.marks_awarded = ans.question.marks
                 score += ans.question.marks
            else:
                 ans.marks_awarded = 0
            ans.save()
            
    attempt.score = score
    attempt.status = 'SUBMITTED'
    attempt.submit_time = timezone.now()
    attempt.save()

    # Log it
    from security.models import AuditLog
    AuditLog.objects.create(
        user=request.user,
        action="Force Submit",
        details=f"Admin forced submission for student '{attempt.student.username}' in exam '{attempt.exam.title}'. Score: {score}"
    )
    
    from django.contrib import messages
    messages.success(request, f"Exam successfully submitted for {attempt.student.username}. Score: {score}")
    
    # Redirect back to student details usually
    return redirect('student_detail_view_id', student_id=attempt.student.id)

@login_required
def get_active_announcements(request):
    """
    API to fetch active announcements.
    Can filter by specific exam_id if provided.
    """
    if not request.user.is_student():
        return JsonResponse({'announcements': []})
        
    from .models import ExamAnnouncement
    from django.db.models import Q
    from django.http import JsonResponse
    import datetime
    
    # Get last 5 minutes only (to avoid old spam on refresh)
    # Actually, let's just get all ACTIVE ones created in last 1 hour
    time_threshold = timezone.now() - datetime.timedelta(hours=1)
    
    exam_id = request.GET.get('exam_id')
    
    query = Q(is_active=True) & Q(created_at__gte=time_threshold)
    
    # Filter by Recipient: Global OR Targeted to this student
    query = query & (Q(recipient__isnull=True) | Q(recipient=request.user))
    
    if exam_id:
        # Filter by Exam: Global OR Specific Exam
        query = query & (Q(exam__isnull=True) | Q(exam_id=exam_id))
    else:
        # Global Only
        query = query & Q(exam__isnull=True)
        
    announcements = ExamAnnouncement.objects.filter(query).order_by('-created_at')
    
    data = []
    for a in announcements:
        data.append({
            'id': a.id,
            'message': a.message,
            'timestamp': a.created_at.strftime("%H:%M"),
            'type': 'info' # Can add type later if needed
        })
        
    return JsonResponse({'announcements': data})

@login_required
def check_exam_status(request, exam_id):
    """
    API to check the current status of the user's exam attempt.
    Reflects admin actions (force-submit, duration changes, logout).
    """
    exam = get_object_or_404(Exam, id=exam_id)
    attempt = StudentExamAttempt.objects.filter(student=request.user, exam=exam).first()
    
    if not attempt:
        return JsonResponse({'status': 'no_attempt'}, status=404)
        
    if attempt.status == 'SUBMITTED':
        # Redirect URL for the student
        from django.urls import reverse
        redirect_url = reverse('view_result', args=[attempt.id])
        return JsonResponse({
            'status': 'submitted',
            'redirect': redirect_url,
            'message': 'This exam has been submitted (possibly by an administrator).'
        })
        
    # Calculate live remaining time (handles admin duration changes)
    now = timezone.now()
    exam_duration_sec = exam.duration_minutes * 60
    elapsed = (now - attempt.start_time).total_seconds()
    
    # Check if time is extended or reduced by admin
    remaining_seconds = max(0, exam_duration_sec - elapsed)
    
    # Clamp to hard end time
    time_to_exam_end = (exam.end_time - now).total_seconds()
    remaining_seconds = min(remaining_seconds, time_to_exam_end)
    remaining_seconds = max(0, remaining_seconds)
    
    return JsonResponse({
        'status': 'in_progress',
        'remaining_seconds': int(remaining_seconds)
    })