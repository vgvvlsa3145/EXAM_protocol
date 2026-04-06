from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min, Count, Q, F, Case, When, Sum, Subquery, OuterRef
from django.db.models.functions import TruncDate
from exams.models import Exam, StudentExamAttempt
from results.models import StudentAnswer
import json

@login_required
def marks_analysis(request):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')

    exam_id = request.GET.get('exam_id')
    selected_date = request.GET.get('date')
    exams = Exam.objects.all().order_by('-start_time')
    
    attempts = StudentExamAttempt.objects.filter(status='SUBMITTED')
    
    selected_exam = None
    if exam_id:
        selected_exam = get_object_or_404(Exam, id=exam_id)
        attempts = attempts.filter(exam=selected_exam)
        
    if selected_date:
        attempts = attempts.annotate(day=TruncDate('submit_time')).filter(day=selected_date)

    attempts = attempts.select_related('student', 'student__student_profile')

    # Basic Metrics
    stats = attempts.aggregate(
        avg_score=Avg('score'),
        max_score=Max('score'),
        min_score=Min('score'),
        total_count=Count('id')
    )
    
    # Pass Percentage (assuming 40% is pass)
    pass_mark = 0
    if selected_exam:
        pass_mark = selected_exam.total_marks * 0.4
    else:
        pass_mark = 40 

    pass_count = attempts.filter(score__gte=pass_mark).count()
    fail_count = stats['total_count'] - pass_count
    pass_percentage = (pass_count / stats['total_count'] * 100) if stats['total_count'] > 0 else 0

    # Score Distribution (Bins)
    distribution = [0, 0, 0, 0, 0]
    for attempt in attempts:
        score_pct = 0
        if selected_exam:
            score_pct = (attempt.score / selected_exam.total_marks) * 100
        else:
            score_pct = attempt.score 
            
        if score_pct <= 20: distribution[0] += 1
        elif score_pct <= 40: distribution[1] += 1
        elif score_pct <= 60: distribution[2] += 1
        elif score_pct <= 80: distribution[3] += 1
        else: distribution[4] += 1

    # Toppers (Top 10)
    toppers = attempts.order_by('-score')[:10]
    for topper in toppers:
        topper.percentage = (topper.score / topper.exam.total_marks * 100) if topper.exam.total_marks > 0 else 0
    
    # All Attempts for the list
    all_attempts = attempts.order_by('-score')
    for att in all_attempts:
        att.percentage = (att.score / att.exam.total_marks * 100) if att.exam.total_marks > 0 else 0
        att.is_pass = att.score >= (att.exam.total_marks * 0.4)

    # Global Total Marks for calculations if no exam selected
    total_marks_val = selected_exam.total_marks if selected_exam else (Exam.objects.aggregate(Max('total_marks'))['total_marks__max'] or 100)

    # 1. Date-wise Analysis (Line Chart)
    date_stats_qs = attempts.annotate(date=TruncDate('submit_time')) \
                           .values('date') \
                           .annotate(
                               avg=Avg('score'), 
                               count=Count('id'),
                               passed=Count('id', filter=Q(score__gte=selected_exam.total_marks * 0.4 if selected_exam else 40))
                           ) \
                           .order_by('date')
    
    date_labels = [d['date'].strftime('%b %d') for d in date_stats_qs]
    date_avg_scores = [round(d['avg'], 2) for d in date_stats_qs]
    date_counts = [d['count'] for d in date_stats_qs]
    
    # Summary table for dates
    date_table = []
    for d in date_stats_qs:
        pass_rate = (d['passed'] / d['count'] * 100) if d['count'] > 0 else 0
        date_table.append({
            'date': d['date'],
            'count': d['count'],
            'avg': round(d['avg'], 2),
            'pass_rate': round(pass_rate, 1)
        })

    # 2. Exam Comparison Analysis (Bar Chart)
    exam_comparison = []
    if not selected_exam:
        # Compare all exams
        exam_perf = StudentExamAttempt.objects.filter(status='SUBMITTED') \
                                              .values('exam__title') \
                                              .annotate(avg=Avg('score'), max=Max('score'), count=Count('id')) \
                                              .order_by('-avg')
        exam_comparison = list(exam_perf)
    
    exam_labels = [e['exam__title'] for e in exam_comparison]
    exam_avg_scores = [round(e['avg'], 2) for e in exam_comparison]

    # Unique dates for the filter
    available_dates = StudentExamAttempt.objects.filter(status='SUBMITTED') \
        .annotate(day=TruncDate('submit_time')) \
        .values_list('day', flat=True) \
        .distinct() \
        .order_by('-day')

    context = {
        'exams': exams,
        'selected_exam': selected_exam,
        'selected_date': selected_date,
        'available_dates': available_dates,
        'stats': stats,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'pass_percentage': round(pass_percentage, 2),
        'toppers': toppers,
        'all_attempts': all_attempts,
        'dist_data': json.dumps(distribution),
        'labels': json.dumps(['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']),
        'total_marks_val': total_marks_val,
        # New charts data
        'date_labels': json.dumps(date_labels),
        'date_avg_scores': json.dumps(date_avg_scores),
        'date_counts': json.dumps(date_counts),
        'date_table': date_table,
        'exam_labels': json.dumps(exam_labels),
        'exam_avg_scores': json.dumps(exam_avg_scores),
    }
    
    return render(request, 'analytics/marks_analysis.html', context)

@login_required
def export_analysis_csv(request):
    import csv
    from django.http import HttpResponse
    
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    exam_id = request.GET.get('exam_id')
    
    if exam_id:
        exam = get_object_or_404(Exam, id=exam_id)
        attempts = StudentExamAttempt.objects.filter(exam=exam, status='SUBMITTED').select_related('student', 'student__student_profile')
        filename = f"{exam.title}_analysis_results.csv"
    else:
        attempts = StudentExamAttempt.objects.filter(status='SUBMITTED').select_related('student', 'student__student_profile')
        filename = "all_exams_analysis_results.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Username/Roll No', 'Exam', 'Score', 'Total Marks', 'Percentage', 'Department', 'Date Submitted'])
    
    for att in attempts:
        dept = getattr(att.student.studentprofile, 'department', 'N/A') if hasattr(att.student, 'studentprofile') else 'N/A'
        total = att.exam.total_marks
        pct = (att.score / total * 100) if total > 0 else 0
        
        writer.writerow([
            att.student.get_full_name() or att.student.username,
            att.student.username,
            att.exam.title,
            att.score,
            total,
            f"{pct:.2f}%",
            dept,
            att.submit_time.strftime('%Y-%m-%d %H:%M')
        ])
        
    return response

@login_required
def live_monitoring(request):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    from django.db.models import Subquery, OuterRef
    from django.db.models.functions import Coalesce

    # Subqueries to avoid cartesian product (join explosion)
    answers_qs = StudentAnswer.objects.filter(attempt=OuterRef('pk'))
    
    active_attempts = StudentExamAttempt.objects.filter(status='IN_PROGRESS') \
        .select_related('student', 'exam', 'student__student_profile') \
        .annotate(
            answered_count=Coalesce(Subquery(
                answers_qs.values('attempt').annotate(c=Count('id')).values('c')
            ), 0),
            current_score=Coalesce(Subquery(
                answers_qs.values('attempt').annotate(s=Sum('marks_awarded')).values('s')
            ), 0.0),
            total_questions=Case(
                When(exam__random_question_count__gt=0, then=F('exam__random_question_count')),
                default=Count('exam__questions', distinct=True)
            )
        )
    
    # Refresh logic similar to dashboard
    return render(request, 'analytics/live_monitoring.html', {
        'active_attempts': active_attempts
    })

@login_required
def student_attempt_detail(request, attempt_id):
    if not (request.user.is_staff or request.user.role in ['ADMIN', 'FACULTY']):
        return redirect('dashboard')
        
    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    answers = StudentAnswer.objects.filter(attempt=attempt).select_related('question', 'selected_option')
    
    # We need to know which options were available for each question and which is correct
    for ans in answers:
        if ans.question.question_type == 'MCQ':
            ans.question_options = ans.question.options.all()
    
    return render(request, 'analytics/student_attempt_detail.html', {
        'attempt': attempt,
        'answers': answers,
    })
