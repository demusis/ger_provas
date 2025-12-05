from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Exam, StudentSubmission, ExamVersion, ExamQuestion
from routes.auth import login_required
import json
import statistics

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    try:
        # List all exams to select for analysis
        exams = Exam.query.order_by(Exam.id.desc()).all()
        return render_template('dashboard/index.html', exams=exams)
    except Exception as e:
        from flask import flash
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@bp.route('/exam/<int:exam_id>')
@login_required
def exam_stats(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    # Get all submissions for this exam
    submissions = StudentSubmission.query.join(ExamVersion).filter(ExamVersion.exam_id == exam.id).all()
    
    if not submissions:
        return render_template('dashboard/exam_stats.html', exam=exam, no_data=True)
    
    # 1. General Stats
    scores = [s.score for s in submissions if s.score is not None]
    
    if not scores:
         return render_template('dashboard/exam_stats.html', exam=exam, no_data=True)
         
    import math
    
    n = len(scores)
    mean = statistics.mean(scores)
    
    # Standard Deviation (Sample) - requires n > 1
    stdev = statistics.stdev(scores) if n > 1 else 0
    
    skewness = None
    kurtosis = None
    
    if n >= 3 and stdev > 0:
        # Fisher-Pearson coefficient of skewness (G1)
        # Sum((x - mean)^3) / n
        m3_sum = sum((x - mean)**3 for x in scores)
        # G1 = [n / ((n-1)(n-2))] * [Sum((x-mean)^3) / s^3]
        # Or simpler: m3 / s^3 * correction
        
        # Using the standard expanded formula for sample skewness
        skewness = (n * m3_sum) / ((n - 1) * (n - 2) * (stdev**3))
        skewness = round(skewness, 2)

    if n >= 4 and stdev > 0:
        # Sample Excess Kurtosis (G2)
        m4_sum = sum((x - mean)**4 for x in scores)
        
        term1 = (n * (n + 1) * m4_sum) / ((n - 1) * (n - 2) * (n - 3) * (stdev**4))
        term2 = (3 * ((n - 1)**2)) / ((n - 2) * (n - 3))
        kurtosis = term1 - term2
        kurtosis = round(kurtosis, 2)

    # Calculate Cronbach's Alpha (Reliability)
    # Since versions differ, we calculate per version and average.
    
    alpha_values = []
    
    # helper to calculated variance
    def calculate_variance(data):
        n = len(data)
        if n < 2: return 0
        mean = sum(data) / n
        return sum((x - mean) ** 2 for x in data) / (n - 1)

    for version in exam.versions:
        # Get submissions for this version
        v_subs = [s for s in submissions if s.exam_version_id == version.id and s.answers]
        if len(v_subs) < 2:
            continue
            
        # Get all question numbers for this version
        q_nums = sorted([eq.question_number for eq in version.questions])
        k_items = len(q_nums)
        if k_items < 2:
            continue
            
        # Build score matrix: rows=students, cols=items (1 if correct, else 0)
        # We need to parse answers
        
        # item_scores[q_num] = [1, 0, 1, ...]
        item_scores = {qn: [] for qn in q_nums}
        total_scores = []
        
        valid_subs_count = 0
        
        for sub in v_subs:
            try:
                ans_dict = json.loads(sub.answers)
            except:
                continue
                
            # Mapping q_num -> Correct Char
            correct_map = {eq.question_number: eq.correct_option_char for eq in version.questions}
            
            student_item_scores = []
            
            for qn in q_nums:
                correct_char = correct_map.get(qn)
                student_ans = ans_dict.get(str(qn))
                
                score = 1 if student_ans == correct_char else 0
                item_scores[qn].append(score)
                student_item_scores.append(score)
            
            total_scores.append(sum(student_item_scores))
            valid_subs_count += 1
            
        if valid_subs_count < 2:
            continue
            
        # Calculate item variances
        sum_item_variances = sum(calculate_variance(scores) for scores in item_scores.values())
        
        # Calculate total variance
        total_variance = calculate_variance(total_scores)
        
        if total_variance > 0:
            # Alpha formula: (K / (K-1)) * (1 - (Sum_Var_i / Var_Total))
            alpha = (k_items / (k_items - 1)) * (1 - (sum_item_variances / total_variance))
            alpha_values.append(alpha)

    avg_alpha = None
    if alpha_values:
        avg_alpha = sum(alpha_values) / len(alpha_values)
        avg_alpha = round(avg_alpha, 2)


    stats = {
        'count': n,
        'average': round(mean, 2),
        'median': round(statistics.median(scores), 2),
        'min': round(min(scores), 2),
        'max': round(max(scores), 2),
        'stdev': round(stdev, 2),
        'skewness': skewness if skewness is not None else "N/A",
        'kurtosis': kurtosis if kurtosis is not None else "N/A",
        'alpha': avg_alpha if avg_alpha is not None else "N/A"
    }
    
    # 2. Grade Distribution (Histogram)
    max_val = exam.max_grade if exam.max_grade else 10.0
    num_bins = 5
    bin_size = max_val / num_bins
    
    buckets = [0] * num_bins
    labels = []
    
    # Generate labels
    for i in range(num_bins):
        start = i * bin_size
        end = (i + 1) * bin_size
        # Format label cleanly: remove .0 if integer
        s_lbl = f"{start:.0f}" if start.is_integer() else f"{start:.1f}"
        e_lbl = f"{end:.0f}" if end.is_integer() else f"{end:.1f}"
        labels.append(f"{s_lbl}-{e_lbl}")
        
    for score in scores:
        # Avoid division by zero if something weird happens (though max_val defaults to 10)
        if bin_size > 0:
            idx = int(score / bin_size)
            if idx >= num_bins:
                idx = num_bins - 1
            if idx < 0:
                idx = 0
            buckets[idx] += 1
        else:
            # Fallback if bin_size is 0 (max_grade=0)
            buckets[0] += 1
        
    distribution_data = {
        'labels': labels,
        'data': buckets
    }
    
    # 3. Question Analysis
    # We need to aggregate results per question.
    # Since questions are shuffled, we need to map back to the original Question ID.
    
    # Create top/bottom groups for Discrimination Index
    # Sort submissions by score descending
    sorted_subs = sorted([s for s in submissions if s.score is not None], key=lambda x: x.score, reverse=True)
    n_subs = len(sorted_subs)
    
    # 27% rule is standard for discrimination index
    n_group = math.ceil(n_subs * 0.27)
    
    top_group_ids = {s.id for s in sorted_subs[:n_group]}
    # If n_subs is small, bottom group might overlap if we are not careful, but typically bottom is last n_group
    # If n_subs < 2, discrimination is undefined.
    bottom_group_ids = {s.id for s in sorted_subs[-n_group:]} if n_subs >= 2 else set()
    
    question_stats = {} # {question_id: {'statement': str, 'correct': int, 'total': int, 'weight': float}}
    
    for sub in submissions:
        if not sub.answers:
            continue
            
        try:
            answers = json.loads(sub.answers) # {'1': 'A', '2': 'C'...} - keys are question numbers in THAT version
        except json.JSONDecodeError:
            continue
            
        version = sub.version
        
        # Get mapping for this version: question_number -> ExamQuestion
        version_questions = {eq.question_number: eq for eq in version.questions}
        
        is_top = sub.id in top_group_ids
        is_bottom = sub.id in bottom_group_ids
        
        for q_num_str, student_ans in answers.items():
            q_num = int(q_num_str)
            if q_num in version_questions:
                eq = version_questions[q_num]
                q_id = eq.question_id
                
                if q_id not in question_stats:
                    question_stats[q_id] = {
                        'id': q_id,
                        'statement': eq.question.statement[:100] + '...' if len(eq.question.statement) > 100 else eq.question.statement,
                        'correct_count': 0,
                        'total_count': 0,
                        'weight': eq.question.weight,
                        'top_correct': 0,
                        'top_total': 0,
                        'bottom_correct': 0,
                        'bottom_total': 0
                    }
                
                stats_q = question_stats[q_id]
                stats_q['total_count'] += 1
                
                if is_top: stats_q['top_total'] += 1
                if is_bottom: stats_q['bottom_total'] += 1
                
                if student_ans == eq.correct_option_char:
                    stats_q['correct_count'] += 1
                    if is_top: stats_q['top_correct'] += 1
                    if is_bottom: stats_q['bottom_correct'] += 1

    # Calculate percentages
    analysis_list = []
    for q_id, data in question_stats.items():
        total = data['total_count']
        correct = data['correct_count']
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        # Discrimination Index
        # D = P_top - P_bottom
        d_index = "N/A"
        if data['top_total'] > 0 and data['bottom_total'] > 0:
            p_top = data['top_correct'] / data['top_total']
            p_bottom = data['bottom_correct'] / data['bottom_total']
            d_index = round(p_top - p_bottom, 2)
        
        analysis_list.append({
            'id': data['id'],
            'statement': data['statement'],
            'total': total,
            'correct': correct,
            'accuracy': round(accuracy, 1),
            'error_rate': round(100 - accuracy, 1),
            'discrimination': d_index
        })
        
    # Sort by Error Rate (Desc) - Hardest questions first
    # Sort by Error Rate (Desc) - Hardest questions first
    analysis_list.sort(key=lambda x: x['error_rate'], reverse=True)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_items = len(analysis_list)
    total_pages = (total_items + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_questions = analysis_list[start:end]
    
    return render_template('dashboard/exam_stats.html', 
                           exam=exam, 
                           stats=stats, 
                           distribution=distribution_data, 
                           questions=paginated_questions,
                           current_page=page,
                           total_pages=total_pages)
